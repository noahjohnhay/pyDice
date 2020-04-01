# coding=utf-8

import json
from functools import reduce

import requests
from logbook import Logger
from py_dice import common, dice10k, slack_api

log = Logger(__name__)


def join_game(game_info: dict, payload: dict) -> dict:
    username = payload["user"]["username"]
    if username not in game_info["users"]:
        game_info["users"][username] = {
            "user_id": dice10k.add_player(game_info["game_id"], username)["player-id"],
            "slack_id": payload["user"]["id"],
        }
        slack_api.producers.respond_in_thread(
            game_info, f"@{username} has successfully joined the game"
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
    slack_api.producers.respond_roll(game_info, response["game-state"]["turn-player"])
    return None


def pick_dice(game_info: dict, response_url: str, username: str, payload: dict):
    log.debug("Action: Picked Dice")
    roll = reduce(common.fetch_die_val, payload["actions"][0]["selected_options"], [])
    response = dice10k.send_keepers(
        game_info["game_id"], game_info["users"][username]["user_id"], roll
    )
    ice_broken = False
    for x in response["game-state"]["players"]:
        log.info(x)
        if x["name"] == username:
            log.info("found ice state")
            ice_broken = x["ice-broken?"]
            current_points = x["points"]
            break
    if response["message"] == "Must pick at least one scoring die":
        requests.post(
            url=response_url,
            json=slack_api.producers.build_slack_message(
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
        slack_api.producers.respond_in_thread(
            game_info,
            f"@{username}\n"
            f"Picked: {roll}\n"
            f"Pending Points: {response['pending-points']}, Current Points {current_points}\n"
            f"Remaining Dice: {response['game-state']['pending-dice']}\n"
            f"Ice Broken: {ice_broken}",
        )
        if not (ice_broken or response.get("pending-points", 0) >= 1000):
            roll_dice(game_info=game_info, response_url=response_url, username=username)
        else:
            slack_api.producers.pass_roll_survey(
                game_info, username, response, ice_broken
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
    slack_api.producers.respond_roll(game_info=game_info, username=username)
    return None


def start_game(game_info: dict, response_url: str):
    log.debug("Action: Started Game")
    start_response = dice10k.start_game(game_info["game_id"])
    turn_player = start_response["turn-player"]
    log.debug(f"Its this players turn: {turn_player}")
    log.debug(f"Start game response: {json.dumps(start_response, indent=2)}")
    requests.post(
        url=response_url,
        json={
            "replace_original": "true",
            "type": "mrkdwn",
            "text": "*=====================================*\n"
            "*Game has started, follow in thread from now on*\n"
            "*=====================================*",
        },
    )
    slack_api.producers.respond_roll(game_info, turn_player)
    return
