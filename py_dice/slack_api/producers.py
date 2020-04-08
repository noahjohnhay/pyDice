# coding=utf-8

import os

import requests
from logbook import Logger
from py_dice import common, dataclasses, dice10k, slack_api
from slack import WebClient

log = Logger(__name__)
auto_break = True


def create_client() -> WebClient:
    slack_token = os.environ["SLACK_API_TOKEN"]
    slack_client = WebClient(token=slack_token)
    return slack_client


def delete_message(channel: str, ts: str) -> None:
    try:
        requests.post(url=ts, json={"delete_original": True})
    except Exception as e:
        log.error(e)
    return None


def roll_with_player_message(
    slack_client: WebClient, game_info: dict, username: str, steal: bool = False
) -> None:
    roll_response = dice10k.roll(
        game_id=game_info["game_id"],
        user_id=game_info["users"][username]["user_id"],
        steal=steal,
    )
    roll = roll_response["roll"]
    if roll_response["message"] == "Pick Keepers!":
        send_roll_message(
            slack_client=slack_client,
            game_info=game_info,
            username=username,
            action="rolled",
            roll=roll,
        )
        slack_client.chat_postEphemeral(
            **dataclasses.message.create(
                game_info["game_id"],
                game_info["channel"],
                f"You rolled: {common.format_dice_emojis(roll)}",
            )
            .at_user(slack_id=game_info["users"][username]["slack_id"])
            .in_thread(thread_id=game_info["parent_message_ts"])
            .pick_die(roll_val=roll)
            .build()
        )
        if auto_break and game_info["users"][username]["broken_int"] == 0:
            slack_api.actions.pick_dice(
                slack_client=slack_client,
                game_info=game_info,
                message_id="1586140914.031800",
                username=username,
                picks=roll,
            )
    elif roll_response["message"] == "You Busted!":
        next_player = roll_response["game-state"]["turn-player"]
        send_roll_message(
            slack_client=slack_client,
            game_info=game_info,
            username=username,
            action="BUSTED!",
            roll=roll,
        )
        roll_with_player_message(
            slack_client=slack_client, game_info=game_info, username=next_player
        )
    else:
        slack_client.chat_postMessage(
            **dataclasses.message.create(
                game_id=game_info["game_id"],
                channel_id=game_info["channel"],
                message="We encountered and error, Please try another time",
            )
            .in_thread(game_info["parent_message_ts"])
            .build()
        )
        log.warn("The API returned an unknown message for your roll")
    return None


def send_roll_message(
    slack_client: WebClient, game_info: dict, username: str, action: str, roll
) -> None:
    slack_client.chat_postMessage(
        **dataclasses.message.create(
            game_id=game_info["game_id"],
            channel_id=game_info["channel"],
            message=f"@{username} {action}: {common.format_dice_emojis(roll)}",
        )
        .at_user(slack_id=game_info["users"][username]["slack_id"])
        .in_thread(thread_id=game_info["parent_message_ts"])
        .build()
    )
    return None


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
