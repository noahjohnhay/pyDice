# coding=utf-8

import json
import os
from functools import reduce

import requests
import slack
from logbook import Logger
from py_dice import common, dice10k

log = Logger(__name__)

slack_token = os.environ["SLACK_API_TOKEN"]
client = slack.WebClient(token=slack_token)
log.debug("STARTING THE CLIENT AGAIN")


def build_options(acc: list, x: int) -> list:
    acc.append(
        {
            "text": {"type": "plain_text", "text": f":die{x}:"},
            "value": f"value-{len(acc) + 1}",
        }
    )
    return acc


def build_slack_message(
    roll_val: list, message: str, pickable: bool, game_dict: dict, username: str
) -> dict:
    log.debug(game_dict["game_id"])

    params = {
        "blocks": [
            {
                "type": "section",
                "block_id": game_dict["game_id"],
                "text": {"type": "mrkdwn", "text": message},
            }
        ],
        "channel": game_dict["channel"],
        "thread_ts": game_dict["message_ts"],
        "user": game_dict["users"][username]["slack_id"],
        "accessory": {},
    }
    if pickable:
        params["blocks"][0]["accessory"] = {
            "action_id": "pick_die",
            "type": "multi_static_select",
            "placeholder": {"type": "plain_text", "text": "Pick to keep"},
            "options": reduce(build_options, roll_val, []),
        }
    log.debug(json.dumps(params, indent=2))
    return params


def respond_in_thread(game_dict: dict, text: str) -> dict:
    params = {
        "blocks": [
            {
                "type": "section",
                "block_id": game_dict["game_id"],
                "text": {"type": "mrkdwn", "text": text},
            }
        ],
        "channel": game_dict["channel"],
        "thread_ts": game_dict["message_ts"],
    }
    log.debug(json.dumps(params, indent=2))
    send_message(params)
    return params


def pass_roll_survey(game_info: dict, username: str, payload: dict, response: dict, ice_broken: bool):
    params = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@{username} would you like to roll or pass",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "roll_dice",
                        "text": {"type": "plain_text", "text": "Roll"},
                        "value": game_info["game_id"],
                    }
                ],
            },
        ],
        "channel": game_info["channel"],
        "thread_ts": game_info["message_ts"],
        "user": game_info["users"][username]["slack_id"],
    }
    if (
        ice_broken
        or response.get("pending-points", 0) >= 1000
    ):
        params["blocks"][1]["elements"].append(
            {
                "type": "button",
                "action_id": "pass_dice",
                "text": {"type": "plain_text", "text": "Pass"},
                "value": game_info["game_id"],
            }
        )
    log.debug(json.dumps(params, indent=2))
    return client.chat_postEphemeral(**params)


def join_game_survey(user, game_id):
    params = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@{user} started a game, click to join:",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "join_game",
                        "text": {"type": "plain_text", "text": "Join Game"},
                        "value": game_id,
                    },
                    {
                        "type": "button",
                        "action_id": "start_game",
                        "text": {"type": "plain_text", "text": "Start Game"},
                        "style": "danger",
                        "confirm": {
                            "title": {"type": "plain_text", "text": "Are You Sure?"},
                            "text": {
                                "type": "mrkdwn",
                                "text": "Has everyone joined the game?",
                            },
                            "confirm": {"type": "plain_text", "text": "Start Game!"},
                            "deny": {"type": "plain_text", "text": "Cancel"},
                        },
                        "value": game_id,
                    },
                ],
            },
        ]
    }
    log.debug(json.dumps(params, indent=2))
    return send_message(params)


def respond_roll(game_dict: dict, username):
    roll_response = dice10k.manage.roll(
        game_dict["game_id"], game_dict["users"][username]["user_id"]
    )
    log.debug(json.dumps(roll_response, indent=2))
    roll = roll_response["roll"]
    if roll_response["message"] == "Pick Keepers!":
        blah(game_dict, username, "rolled", roll)
        client.chat_postEphemeral(
            **build_slack_message(
                roll,
                f"You rolled: {common.format_dice_emojis(roll)}",
                True,
                game_dict,
                username,
            )
        )
    elif roll_response["message"] == "You Busted!":
        next_player = roll_response["game-state"]["turn-player"]
        blah(game_dict, username, "BUSTED!", roll)
        respond_roll(game_dict, next_player)
    else:
        respond_in_thread(
            game_dict, "We encountered and error, Please try another time"
        )
        return log.error("The API returned an unknown message for your roll")

    return ""


def blah(game_dict, username, action, roll):
    send_message(
        build_slack_message(
            roll,
            f"@{username} {action}: {common.format_dice_emojis(roll)}",
            False,
            game_dict,
            username,
        )
    )


def send_message(params: dict) -> requests.Response:
    response = requests.post(os.environ["slack_url"], json=params)
    log.debug(response.content)
    return response
