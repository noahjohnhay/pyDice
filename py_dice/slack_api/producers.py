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


def roll_with_player_message(game_info: dict, username: str):
    roll_response = dice10k.roll(
        game_info["game_id"], game_info["users"][username]["user_id"]
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
        log.error("The API returned an unknown message for your roll")
    return ""


def send_roll_message(game_dict: dict, username: str, action: str, roll):
    send_message(
        slack_api.bodies.build_slack_message(
            roll,
            f"@{username} {action}: {common.format_dice_emojis(roll)}",
            False,
            game_dict,
            username,
        )
    )


def send_message(params: dict) -> dict:
    response = requests.post(url=os.environ["slack_url"], json=params).content
    return response


def update_parent_message(title_message_url: str, game_id):
    # list of users and their current scores
    # username: send_roll_message
    # current score
    current_game_info = dice10k.fetch_game(game_id)
    log.error(current_game_info)
    user_str = ""
    for user in current_game_info["players"]:
        string = f"{user['name']}'s score: {user['points']}"
        if user["ice-broken?"]:
            string += f": *ICE BROKEN!*"
        user_str += f"{string}\n"
    requests.post(
        title_message_url,
        json={
            "replace_original": "true",
            "type": "mrkdwn",
            "text": "*=====================================*\n"
            "*Game has started, follow in thread from now on*\n"
            f"{user_str}"
            "*=====================================*",
        },
    )
