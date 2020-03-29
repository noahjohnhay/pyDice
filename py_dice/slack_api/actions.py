# coding=utf-8

import json
from functools import reduce

import requests
from logbook import Logger
from py_dice import common, dice10k, slack_api

log = Logger(__name__)


def join_game(game_state: dict, payload: dict) -> dict:
    log.debug("Action: Joined game")
    game_id = payload["actions"][0]["value"]
    log.info(payload)
    username = payload["user"]["username"]
    if username not in game_state[game_id]["users"]:
        game_state[game_id]["users"][username] = {
            "user_id": dice10k.manage.add_player(game_id, username)["player-id"],
            "slack_id": payload["user"]["id"],
        }
        slack_api.producers.respond_in_thread(
            game_state[game_id], f"@{username} has successfully joined the game"
        )
    log.debug(f"Game state: {json.dumps(game_state, indent=2)}")
    return game_state


def pass_dice():
    log.debug("Action: Passed dice")
    return


def pick_dice(payload: dict, game_dict: dict):
    log.debug("Action: Picked dice")
    username = payload["user"]["username"]
    roll = reduce(common.fetch_die_val, payload["actions"][0]["selected_options"], [])

    response = dice10k.manage.send_keepers(
        game_dict["game_id"], game_dict["users"][username]["user_id"], roll
    )

    if response["message"] == "Must pick at least one scoring die":
        requests.post(
            payload["response_url"],
            json=slack_api.producers.build_slack_message(
                response["roll"],
                f'{response["message"]}, try again: {common.format_dice_emojis(response["roll"])}',
                True,
                game_dict,
                username,
            ),
        )
    else:
        requests.post(payload["response_url"], json={"delete_original": True})
        roll = common.format_dice_emojis(
            reduce(common.fetch_die_val, payload["actions"][0]["selected_options"], [])
        )
        slack_api.producers.respond_in_thread(
            game_dict,
            f"@{username}\n"
            f"Picked: {roll}\n"
            f"Pending Points: {response['pending-points']}\n"
            f"Remaining Dice: {response['game-state']['pending-dice']}",
        )
        slack_api.producers.pass_roll_survey(game_dict, username)
    return


def roll_dice(game_info, username):

    log.info("Action: rolled dice")
    slack_api.producers.respond_roll(game_info, username)
    return


def start_game(payload: dict, game_dict):
    log.debug("Action: Started game")
    start_response = dice10k.manage.start_game(payload["actions"][0]["value"])
    turn_player = start_response["turn-player"]
    log.debug(f"Its this players turn:: {turn_player}")
    log.debug(f"Start game response: " f"{json.dumps(start_response, indent=2)}")
    requests.post(
        payload["response_url"],
        json={
            "replace_original": "true",
            "type": "mrkdwn",
            "text": "*=====================================*\n"
            "*Game has started, follow in thread from now on*\n"
            "*=====================================*",
        },
    )
    slack_api.producers.respond_roll(game_dict, turn_player)

    return
