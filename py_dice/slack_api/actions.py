# coding=utf-8

import json
import os
from functools import reduce

import requests
import slack
from logbook import Logger
from py_dice import common, dice10k, slack_api

log = Logger(__name__)

slack_token = os.environ["SLACK_API_TOKEN"]
client = slack.WebClient(token=slack_token)
log.debug("STARTING THE CLIENT AGAIN")


def join_game(game_info: dict, slack_user_id: str, username: str) -> dict:
    if username not in game_info["users"]:
        game_info["users"][username] = {
            "user_id": dice10k.add_player(game_info["game_id"], username)["player-id"],
            "slack_id": slack_user_id,
        }
        client.chat_postMessage(
            **slack_api.bodies.respond_in_thread(
                game_info, f"@{username} has successfully joined the game"
            )
        )

    return game_info


def pass_dice(game_info: dict, response_url: str, username: str) -> None:
    """
    Description:
        Pass dice action
    Args:
        game_info: dict
        response_url: str
        username: str
    Returns:
        None
    """
    log.debug("Action: Pass Dice")
    requests.post(url=response_url, json={"delete_original": True})
    response = dice10k.pass_turn(
        game_id=game_info["game_id"], user_id=game_info["users"][username]["user_id"]
    )
    slack_api.producers.roll_with_player_message(
        game_info, response["game-state"]["turn-player"]
    )
    slack_api.producers.update_parent_message(
        game_info["title_message_url"], game_info["game_id"]
    )
    return None


def pick_dice(game_info: dict, response_url: str, username: str, payload: dict):
    log.debug("Action: Picked Dice")
    roll = reduce(common.fetch_die_val, payload["actions"][0]["selected_options"], [])
    response = dice10k.send_keepers(
        game_info["game_id"], game_info["users"][username]["user_id"], roll
    )
    ice_broken = False
    if response["message"] == "Must pick at least one scoring die":
        requests.post(
            url=response_url,
            json=slack_api.bodies.build_slack_message(
                response["roll"],
                f'{response["message"]}, try again: {common.format_dice_emojis(response["roll"])}',
                True,
                game_info,
                username,
            ),
        )
    else:
        requests.post(url=response_url, json={"delete_original": True})
        roll = common.format_dice_emojis(
            reduce(common.fetch_die_val, payload["actions"][0]["selected_options"], [])
        )
        client.chat_postMessage(
            **slack_api.bodies.respond_in_thread(
                game_info,
                f"@{username}\n"
                f"Picked: {roll}\n"
                f"Pending Points: {response['pending-points']}\n"
                f"Remaining Dice: {response['game-state']['pending-dice']}\n",
            )
        )

        if not (ice_broken or response.get("pending-points", 0) >= 1000):
            roll_dice(game_info=game_info, response_url=response_url, username=username)
        else:
            client.chat_postEphemeral(
                **slack_api.bodies.pass_roll_survey(
                    game_info=game_info,
                    username=username,
                    response=response,
                    ice_broken=ice_broken,
                )
            )
    return


def roll_dice(game_info: dict, response_url: str, username: str) -> None:
    """
    Description:
        Roll dice action
    Args:
        game_info: dict
        response_url: str
        username: str
    Returns:
        None
    """
    log.debug("Action: Rolled Dice")
    requests.post(url=response_url, json={"delete_original": True})
    slack_api.producers.roll_with_player_message(game_info=game_info, username=username)
    return None


def start_game(game_info: dict, response_url: str):
    log.debug("Action: Started Game")
    start_response = dice10k.start_game(game_info["game_id"])
    turn_player = start_response["turn-player"]
    log.debug(f"Its this players turn: {turn_player}")
    log.debug(f"Start game response: {json.dumps(start_response, indent=2)}")
    game_info["title_message_url"] = response_url
    slack_api.producers.update_parent_message(response_url, game_info["game_id"])
    slack_api.producers.roll_with_player_message(game_info, turn_player)
    return game_info
