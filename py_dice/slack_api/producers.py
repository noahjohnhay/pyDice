# coding=utf-8

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


def build_options(options: list, die_number: int) -> list:
    options.append(
        {
            "text": {"type": "plain_text", "text": f":die{die_number}:"},
            "value": f"value-{len(options) + 1}",
        }
    )
    return options


def build_slack_message(
    roll_val: list, message: str, pickable: bool, game_info: dict, username: str
) -> dict:
    params = {
        "blocks": [
            {
                "type": "section",
                "block_id": game_info["game_id"],
                "text": {"type": "mrkdwn", "text": message},
            }
        ],
        "channel": game_info["channel"],
        "thread_ts": game_info["message_ts"],
        "user": game_info["users"][username]["slack_id"],
        "accessory": {},
    }
    if pickable:
        params["blocks"][0]["accessory"] = {
            "action_id": "pick_die",
            "type": "multi_static_select",
            "placeholder": {"type": "plain_text", "text": "Pick to keep"},
            "options": reduce(build_options, roll_val, []),
        }
    return params


def respond_in_thread(game_info: dict, message: str) -> dict:
    """
    Description:
        Post message in thread
    Args:
        game_info: dict
        message: str
    Returns
        dict - Response content from posting the message
    """
    params = {
        "blocks": [
            {
                "type": "section",
                "block_id": game_info["game_id"],
                "text": {"type": "mrkdwn", "text": message},
            }
        ],
        "channel": game_info["channel"],
        "thread_ts": game_info["message_ts"],
    }
    return send_message(params)


def pass_roll_survey(game_info: dict, username: str, response: dict, ice_broken: bool):
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
    if ice_broken or response.get("pending-points", 0) >= 1000:
        params["blocks"][1]["elements"].append(
            {
                "type": "button",
                "action_id": "pass_dice",
                "text": {"type": "plain_text", "text": "Pass"},
                "value": game_info["game_id"],
            }
        )
    return client.chat_postEphemeral(**params)


def join_game_survey(game_id: str, username: str) -> dict:
    """
    Description:
        Ask players to join the game
    Args:
        game_id: str
        username: str
    Returns:
        dict - Response content from posting the message
    """
    params = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@{username} started a game, click to join:",
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
    return send_message(params)


def respond_roll(game_info: dict, username: str):
    roll_response = dice10k.roll(
        game_info["game_id"], game_info["users"][username]["user_id"]
    )
    roll = roll_response["roll"]
    if roll_response["message"] == "Pick Keepers!":
        blah(game_info, username, "rolled", roll)
        client.chat_postEphemeral(
            **build_slack_message(
                roll,
                f"You rolled: {common.format_dice_emojis(roll)}",
                True,
                game_info,
                username,
            )
        )
    elif roll_response["message"] == "You Busted!":
        next_player = roll_response["game-state"]["turn-player"]
        blah(game_info, username, "BUSTED!", roll)
        respond_roll(game_info=game_info, username=next_player)
    else:
        respond_in_thread(
            game_info=game_info,
            message="We encountered and error, Please try another time",
        )
        log.error("The API returned an unknown message for your roll")
    return ""


def blah(game_dict: dict, username: str, action: str, roll):
    send_message(
        build_slack_message(
            roll,
            f"@{username} {action}: {common.format_dice_emojis(roll)}",
            False,
            game_dict,
            username,
        )
    )


def send_message(params: dict) -> dict:
    response = requests.post(url=os.environ["slack_url"], json=params).content
    log.debug(response.content)
    return response
