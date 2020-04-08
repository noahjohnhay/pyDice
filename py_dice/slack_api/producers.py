# coding=utf-8

import os

import requests
from logbook import Logger
from py_dice import common, dice10k, slack_api
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
        game_info["game_id"], game_info["users"][username]["user_id"], steal
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
            **slack_api.bodies.build_slack_message(
                roll_val=roll,
                message=f"You rolled: {common.format_dice_emojis(roll)}",
                pickable=True,
                game_info=game_info,
                username=username,
            )
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
            **slack_api.bodies.respond_in_thread(
                game_info=game_info,
                message="We encountered and error, Please try another time",
            )
        )
        log.warn("The API returned an unknown message for your roll")
    return None


def send_roll_message(
    slack_client: WebClient, game_info: dict, username: str, action: str, roll
) -> None:
    slack_client.chat_postMessage(
        **slack_api.bodies.build_slack_message(
            roll_val=roll,
            message=f"@{username} {action}: {common.format_dice_emojis(roll)}",
            pickable=False,
            game_info=game_info,
            username=username,
        )
    )
    return None
