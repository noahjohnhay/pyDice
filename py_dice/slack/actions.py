# coding=utf-8

import json

import requests
from logbook import Logger
from py_dice import dice10k, slack

log = Logger(__name__)


def join_game(game_state: dict, payload: dict, user: str):
    log.info("Action: Joined game")
    game_id = payload["actions"][0]["value"]
    if user not in game_state[game_id]["users"]:
        game_state[game_id]["users"][user] = {
            "user_id": dice10k.manage.add_player(game_id, user)["player-id"]
        }
        slack.producers.send_requests(slack.producers.build_join_response(user))
    log.debug(f"Game state: {json.dumps(game_state, indent=2)}")
    return


def role_dice():
    log.info("Action: rolled dice")
    return


def pass_dice():
    log.info("Action: Passed dice")
    return


def pick_dice(payload: dict):
    log.info("Action: Picked dice")
    log.debug(
        f"Pick dice response: {requests.post(payload['response_url'], json={'delete_original': True})}"
    )
    slack.producers.send_picks(
        payload["actions"][0]["selected_options"], payload["user"]["username"]
    )
    return


def start_game(payload: dict):
    log.info("Action: Started game")
    log.debug(
        f"Start game response: "
        f"{json.dumps(dice10k.manage.start_game(payload['actions'][0]['value']), indent=2)}"
    )
    requests.post(
        payload["response_url"],
        json={
            "replace_original": "true",
            "text": "Game Has Been Started, hope Calin Joined :)",
        },
    )
    return
