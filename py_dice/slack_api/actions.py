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
            "broken_int": 0,
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

    """
    {
       'message': 'Successful pass.',
       'pending-points': 1000,
       'game-state': {
                    'game-id': '3c0771d4-b7bc-4580-9118-ab0d7349b738',
                    'players': [{'name': 'jonathan.armel.daigle',
                                    'turn-order': 0,
                                     'points': 1000,
                                     'turn-seq': 0,
                                     'pending-points': 0,
                                     'ice-broken?': True,
                                     'roll-vec': []}],
        'friendly-name':
        'fragmentates wage',
        'turn': 2,
        'state': 'started',
        'pending-points': 0,
        'pending-dice': 6,
        'turn-player': 'jonathan.armel.daigle'}}
    """
    log.error("Action: Pass Dice")
    requests.post(url=response_url, json={"delete_original": True})
    response = dice10k.pass_turn(
        game_id=game_info["game_id"], user_id=game_info["users"][username]["user_id"]
    )
    log.error(response)
    turn_player = response["game-state"]["turn-player"]
    steal_able = False
    log.error(game_info)
    for x in response["game-state"]["players"]:
        if (
            x["name"] == turn_player
            and x["ice-broken?"]
            and game_info["users"][username]["broken_int"] > 1
        ):
            steal_able = True
    if steal_able:
        log.error("Trigger steal message")
        client.chat_postEphemeral(
            **slack_api.bodies.steal_roll_survey(
                game_info, response["game-state"]["turn-player"]
            )
        )
    else:
        log.error(response)
        slack_api.producers.roll_with_player_message(game_info, turn_player)
    client.chat_update(**slack_api.bodies.update_parent_message(game_info))
    return None


def pick_dice(game_info: dict, response_url: str, username: str, payload: dict):
    log.debug("Action: Picked Dice")
    roll = reduce(common.fetch_die_val, payload["actions"][0]["selected_options"], [])
    response = dice10k.send_keepers(
        game_info["game_id"], game_info["users"][username]["user_id"], roll
    )
    ice_broken = False
    if response["message"] == "Must pick at least one scoring die":
        client.chat_postMessage(
            **slack_api.bodies.build_slack_message(
                response["roll"],
                f'{response["message"]}, try again: {common.format_dice_emojis(response["roll"])}',
                True,
                game_info,
                username,
            )
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
            game_info["users"][username]["broken_int"] += 1
            client.chat_postEphemeral(
                **slack_api.bodies.pass_roll_survey(
                    game_info=game_info,
                    username=username,
                    response=response,
                    ice_broken=ice_broken,
                )
            )
    return game_info


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


def steal_dice(game_info: dict, response_url: str, username: str) -> None:
    log.error("function does nothing yet")
    log.debug(response_url)
    steal_response = dice10k.steal(
        game_info["game_id"], game_info["users"][username]["user_id"]
    )
    log.error(steal_response)
    return steal_response


def start_game(game_info: dict, response_url: str):
    log.debug("Action: Started Game")
    start_response = dice10k.start_game(game_info["game_id"])
    turn_player = start_response["turn-player"]
    log.debug(f"Its this players turn: {turn_player}")
    log.debug(f"Start game response: {json.dumps(start_response, indent=2)}")
    game_info["title_message_url"] = response_url
    response = client.chat_update(
        **slack_api.bodies.update_parent_message(game_info=game_info)
    )
    log.error(response)
    slack_api.producers.roll_with_player_message(game_info, turn_player)
    return game_info
