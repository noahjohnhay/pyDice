# coding=utf-8

import re
from functools import reduce

import requests


def format_emojis(x1: str, x2: int) -> str:
    """
    Description:
        Format slack emoji
    Args:
        x1: str -
        x2: int - die number
    Returns:
        str - Formatted slack emoji
    """
    return f"{x1} :die{x2}:"


# function for a reduce
def build_options(acc: list, x: int) -> list:
    acc.append(
        {
            "text": {"type": "plain_text", "text": f":die{x}:"},
            "value": f"value-{len(acc) + 1}",
        }
    )
    return acc


def fetch_die_val(acc: list, x) -> list:
    die = x["text"]["text"]
    acc.append(int(re.search(r"\d+", die).group()))
    return acc


def build_slack_message(roll_val: object, pronoun: object, pickable: object, action: object = "rolled") -> object:
    params = {
        "blocks": [
            {
                "type": "section",
                "block_id": "{gameId}-{rand_val}",
                "text": {
                    "type": "mrkdwn",
                    "text": f'{pronoun} {action}: {reduce(format_emojis, roll_val, "")}',
                },
            }
        ]
    }
    if pickable:
        params["blocks"][0]["accessory"] = {
            "action_id": "pick_die",
            "type": "multi_static_select",
            "placeholder": {"type": "plain_text", "text": "Pick to keep"},
            "options": reduce(build_options, roll_val, []),
        }
    return params


def build_join_response(username) -> dict:
    params = {
        "blocks": [
            {
                "type": "section",
                "block_id": "{gameId}-{rand_val}",
                "text": {
                    "type": "mrkdwn",
                    "text": f'@{username} has successfuly joined the game'
                }
            }
        ]
    }
    return params


def join_game_survey(user, game_id):
    params = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f'@{user} started a game, click to join:'
                }
            },
            {
                "type": "actions",
                "elements": [

                    {
                        "type": "button",
                        "action_id": "join_game",
                        "text": {
                            "type": "plain_text",
                            "text": "Join Game"
                        },
                        "value": game_id
                    },
                    {
                        "type": "button",
                        "action_id": "start_game",

                        "text": {
                            "type": "plain_text",
                            "text": "Start Game"

                        },
                        "style": "danger",
                        "confirm": {
                            "title": {
                                "type": "plain_text",
                                "text": "Has Everyone Joined?"
                            },
                            "text": {
                                "type": "mrkdwn",
                                "text": "dicks"
                            },
                            "confirm": {
                                "type": "plain_text",
                                "text": "Start Game NOW"
                            },
                            "deny": {
                                "type": "plain_text",
                                "text": "Calin is still not joined!"
                            }
                        },
                        "value": game_id
                    }
                ]
            }
        ]
    }
    print(params)
    return send_requests(params)


# def ask_for_players(game_requester: str):
#     params = ""
#     send_requests()
#     return


def respond_slash_command(params: dict, username: str) -> requests.Response:
    roll = [1, 2, 3, 6]
    send_requests(build_slack_message(roll, f"@{username}", False))
    response = requests.post(
        params["response_url"], json=build_slack_message(roll, "You", True)
    )
    return response


def respond_join(params: dict, message_ts: str, channel_id: str) -> requests.Response:
    response = requests.post(
        params["response_url"], json=build_join_response(message_ts, channel_id)
    )
    return response


def send_picks(picks: list, username: str):
    roll = reduce(fetch_die_val, picks, [])
    params = build_slack_message(roll, f"@{username}", False, "picked")
    return send_requests(params)


def send_requests(params: dict) -> requests.Response:
    print(params)
    jon = requests.post("https://hooks.slack.com/services/*", json=params)
    print(jon.content)
    return jon
