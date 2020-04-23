# coding=utf-8

import os

import requests
from logbook import Logger
from prettytable import PrettyTable
from py_dice import actions, common, dcs, dice10k
from slack import WebClient

log = Logger(__name__)


def create_client() -> WebClient:
    slack_token = os.environ["SLACK_API_TOKEN"]
    slack_client = WebClient(token=slack_token)
    return slack_client


def delete_message(response_url: str) -> None:
    try:
        requests.post(url=response_url, json={"delete_original": True})
    except Exception as e:
        log.debug(e)
    return None


def roll_with_player_message(
    slack_client: WebClient, game_info: dict, username: str, steal: bool = False
) -> None:
    roll_response = dice10k.roll(
        game_id=game_info["game_id"],
        user_id=game_info["users"][username]["user_id"],
        steal=steal,
    )
    if roll_response["message"] == "Pick Keepers!":
        roll = roll_response["roll"]
        send_roll_message(
            slack_client=slack_client,
            game_info=game_info,
            username=username,
            action="rolled",
            roll=roll,
        )
        slack_client.chat_postEphemeral(
            **dcs.message.create(
                game_info["game_id"],
                game_info["channel"],
                f"You rolled: {common.format_dice_emojis(roll)}",
            )
            .at_user(slack_id=game_info["users"][username]["slack_id"])
            .in_thread(thread_id=game_info["parent_message_ts"])
            .pick_die(roll_val=roll)
            .build()
        )
        if game_info["auto_break"] and not common.is_robbable(
            game_info["game_id"], username
        ):
            actions.pick_dice(
                slack_client=slack_client,
                game_info=game_info,
                response_url=game_info["parent_message_ts"],
                username=username,
                picks=roll,
            )
    elif roll_response["message"].startswith("BUSTED"):
        roll = roll_response["roll"]
        next_player = roll_response["game-state"]["turn-player"]
        send_roll_message(
            slack_client=slack_client,
            game_info=game_info,
            username=username,
            action="BUSTED!",
            roll=roll,
        )
        roll_with_player_message(
            slack_client=slack_client,
            game_info=game_info,
            username=next_player,
            steal=False,
        )
        # TODO not done. You can't steal, it'll put you over 10k
    elif roll_response["message"] == "You can't steal, it'll put you over 10k":
        slack_client.chat_postEphemeral(
            **dcs.message.create(
                game_id=game_info["game_id"],
                channel_id=game_info["channel"],
                message=f'{roll_response["message"]}',
            )
            .at_user(slack_id=game_info["users"][username]["slack_id"])
            .add_button(
                game_id=game_info["game_id"], text="Roll", action_id="roll_dice"
            )
            .in_thread(thread_id=game_info["parent_message_ts"])
            .build()
        )
    else:
        slack_client.chat_postMessage(
            **dcs.message.create(
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
        **dcs.message.create(
            game_id=game_info["game_id"],
            channel_id=game_info["channel"],
            message=f"@{username} {action}: {common.format_dice_emojis(roll)}",
        )
        .at_user(slack_id=game_info["users"][username]["slack_id"])
        .in_thread(thread_id=game_info["parent_message_ts"])
        .build()
    )
    return None


def build_game_panel(slack_client, game_info: dict, state: str = "started") -> None:
    players = dice10k.fetch_game(game_info["game_id"])["players"]
    scoreboard = PrettyTable()
    title = f"Game has {state}, follow in thread"
    if state == "completed":
        title = f"Game has {state}"
    scoreboard.field_names = [
        "Player",
        "Score",
        "Pending Points",
        "Possible Score",
        "Ice Broken",
    ]
    scoreboard.title = title
    for player in players:
        scoreboard.add_row(
            [
                player["name"],
                player["points"],
                player["pending-points"],
                player["pending-points"] + player["points"],
                player["ice-broken?"],
            ]
        )
    scoreboard = f"```{scoreboard}```"
    print(scoreboard)
    slack_client.chat_update(
        ts=game_info["parent_message_ts"],
        **dcs.message.create(
            game_info["game_id"], game_info["channel"], scoreboard
        ).build(),
    )
    return None
