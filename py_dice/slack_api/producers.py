# coding=utf-8

import os

import requests
import slack
from logbook import Logger
from py_dice import common, dice10k, slack_api

log = Logger(__name__)

slack_token = os.environ["SLACK_API_TOKEN"]
client = slack.WebClient(token=slack_token)
log.debug("STARTING THE CLIENT AGAIN")


auto_break = True


def delete_message(channel: str, ts: str) -> None:
    requests.post(url=ts, json={"delete_original": True})


def roll_with_player_message(game_info: dict, username: str, steal: bool = False):
    roll_response = dice10k.roll(
        game_info["game_id"], game_info["users"][username]["user_id"], steal
    )
    roll = roll_response["roll"]
    if roll_response["message"] == "Pick Keepers!":
        send_roll_message(game_info, username, "rolled", roll)
        client.chat_postEphemeral(
            **slack_api.bodies.build_slack_message(
                roll,
                f"You rolled: {common.format_dice_emojis(roll)}",
                True,
                game_info,
                username,
            )
        )
        if auto_break and game_info["users"][username]["broken_int"] == 0:
            slack_api.actions.pick_dice(
                game_info=game_info,
                message_id="1586140914.031800",
                username=username,
                roll=roll,
            )

    elif roll_response["message"] == "You Busted!":
        next_player = roll_response["game-state"]["turn-player"]
        send_roll_message(game_info, username, "BUSTED!", roll)
        roll_with_player_message(game_info=game_info, username=next_player)
    else:
        client.chat_postMessage(
            **slack_api.bodies.respond_in_thread(
                game_info=game_info,
                message="We encountered and error, Please try another time",
            )
        )
        log.warn("The API returned an unknown message for your roll")
    return ""


def send_roll_message(game_dict: dict, username: str, action: str, roll):
    client.chat_postMessage(
        **slack_api.bodies.build_slack_message(
            roll,
            f"@{username} {action}: {common.format_dice_emojis(roll)}",
            False,
            game_dict,
            username,
        )
    )
