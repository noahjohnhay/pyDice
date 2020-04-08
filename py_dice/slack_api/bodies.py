# coding=utf-8

from functools import reduce

from py_dice import dice10k


def build_options(acc: list, x: int) -> list:
    acc.append(
        {
            "text": {"type": "plain_text", "text": f":die{x}:"},
            "value": f"value-{len(acc) + 1}",
        }
    )
    return acc


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
        "thread_ts": game_info["parent_message_ts"],
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


def join_game_survey(channel_id: str, game_id: str, username: str) -> dict:
    params = {
        "channel": channel_id,
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
        ],
    }
    return params


def pass_roll_survey(game_info: dict, username: str, can_pass: bool) -> dict:
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
        "thread_ts": game_info["parent_message_ts"],
        "user": game_info["users"][username]["slack_id"],
    }
    if can_pass:
        params["blocks"][1]["elements"].append(
            {
                "type": "button",
                "action_id": "pass_dice",
                "text": {"type": "plain_text", "text": "Pass"},
                "value": game_info["game_id"],
            }
        )
    return params


def steal_roll_survey(game_info: dict, username: str) -> dict:
    params = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@{username} would you like to steal or roll",
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
                    },
                    {
                        "type": "button",
                        "action_id": "steal_dice",
                        "text": {"type": "plain_text", "text": "STEAL"},
                        "value": game_info["game_id"],
                    },
                ],
            },
        ],
        "channel": game_info["channel"],
        "thread_ts": game_info["parent_message_ts"],
        "user": game_info["users"][username]["slack_id"],
    }

    return params


def respond_in_thread(game_info: dict, message: str) -> dict:
    params = {
        "blocks": [
            {
                "type": "section",
                "block_id": game_info["game_id"],
                "text": {"type": "mrkdwn", "text": message},
            }
        ],
        "channel": game_info["channel"],
        "thread_ts": game_info["parent_message_ts"],
    }
    return params


def update_parent_message(game_info: dict) -> dict:
    current_game_info = dice10k.fetch_game(game_info["game_id"])
    scoreboard = ""
    for user in current_game_info["players"]:
        string = f"{user['name']}'s score: {user['points']}"
        if user["ice-broken?"]:
            string += f": *ICE BROKEN!*"
        scoreboard += f"{string}\n"
    params = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*=====================================*\n"
                    "*Game has started, follow in thread from now on*\n"
                    f"{scoreboard}"
                    "*=====================================*",
                },
            }
        ],
        "channel": game_info["channel"],
        "ts": game_info["parent_message_ts"],
    }
    return params
