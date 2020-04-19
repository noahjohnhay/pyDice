# coding=utf-8

import py_dice.slack_api.producers
from logbook import Logger
from py_dice import common, dcs, dice10k, slack_api
from slack import WebClient

log = Logger(__name__)


def join_game(
    slack_client: WebClient, game_info: dict, slack_user_id: str, username: str
) -> dict:
    log.info("Action: Join Game")
    if username not in game_info["users"]:
        game_info["users"][username] = {
            "user_id": dice10k.add_player(game_info["game_id"], username)["player-id"],
            "slack_id": slack_user_id,
        }
        slack_client.chat_postMessage(
            **dcs.message.create(
                game_id=game_info["game_id"],
                channel_id=game_info["channel"],
                message=f"@{username} has successfully joined the game",
            )
            .in_thread(game_info["parent_message_ts"])
            .build()
        )
    return game_info


def pass_dice(
    slack_client: WebClient, game_info: dict, message_id: str, username: str
) -> None:
    slack_client.chat_update(
        **py_dice.slack_api.producers.update_parent_message(
            game_info=game_info, state="started"
        )
    )
    log.info("Action: Pass Dice")
    slack_api.producers.delete_message(channel=game_info["channel"], ts=message_id)
    response = dice10k.pass_turn(
        game_id=game_info["game_id"], user_id=game_info["users"][username]["user_id"]
    )
    turn_player = response["game-state"]["turn-player"]
    if turn_player in common.who_can_steal(game_info["game_id"]):
        slack_client.chat_postEphemeral(
            **dcs.message.create(
                game_id=game_info["game_id"],
                channel_id=game_info["channel"],
                message=f"@{turn_player} would you like to steal or roll",
            )
            .at_user(slack_id=game_info["users"][turn_player]["slack_id"])
            .add_button(
                game_id=game_info["game_id"], text="Roll", action_id="roll_dice"
            )
            .add_button(
                game_id=game_info["game_id"], text="Steal", action_id="steal_dice"
            )
            .in_thread(thread_id=game_info["parent_message_ts"])
            .build()
        )
    else:
        slack_api.producers.roll_with_player_message(
            slack_client=slack_client,
            game_info=game_info,
            username=turn_player,
            steal=False,
        )

    return None


def pick_dice(
    slack_client: WebClient,
    game_info: dict,
    message_id: str,
    username: str,
    picks: list,
):
    log.info("Action: Picked Dice")
    response = dice10k.send_keepers(
        game_id=game_info["game_id"],
        user_id=game_info["users"][username]["user_id"],
        picks=picks,
    )
    if response["message"].startswith("PICK FAIL"):
        slack_client.chat_postMessage(
            **dcs.message.create(
                game_id=game_info["game_id"],
                channel_id=game_info["channel"],
                message=f"{response['message']}, try again: {common.format_dice_emojis(response['roll'])}",
            )
            .at_user(slack_id=game_info["users"][username]["slack_id"])
            .in_thread(thread_id=game_info["parent_message_ts"])
            .pick_die(roll_val=response["roll"])
            .build()
        )
    elif response["message"].startswith("It's not your turn"):
        players = dice10k.fetch_game(game_info["game_id"])["players"]
        current_player = next(p for p in players if p["turn-order"] == 0)
        slack_api.producers.roll_with_player_message(
            slack_client=slack_client,
            game_info=game_info,
            username=current_player["name"],
            steal=False,
        )
    else:
        ice_broken = next(
            p for p in response["game-state"]["players"] if p["name"] == username
        )["ice-broken?"]
        slack_api.producers.delete_message(channel=game_info["channel"], ts=message_id)
        slack_client.chat_postMessage(
            **dcs.message.create(
                game_id=game_info["game_id"],
                channel_id=game_info["channel"],
                message=f"@{username}\n"
                f"Picked: {common.format_dice_emojis(picks)}\n"
                f"Pending Points: {response['pending-points']}\n"
                f"Remaining Dice: {response['game-state']['pending-dice']}\n",
            )
            .in_thread(game_info["parent_message_ts"])
            .build()
        )

        if not (ice_broken or response.get("pending-points", 0) >= 1000):

            roll_dice(
                slack_client=slack_client,
                game_info=game_info,
                message_id=message_id,
                username=username,
            )
        else:
            slack_client.chat_postEphemeral(
                **dcs.message.create(
                    game_id=game_info["game_id"],
                    channel_id=game_info["channel"],
                    message=f"@{username} would you like to roll or pass",
                )
                .add_button(
                    game_id=game_info["game_id"], text="Roll", action_id="roll_dice"
                )
                .add_button(
                    game_id=game_info["game_id"], text="Pass", action_id="pass_dice"
                )
                .at_user(slack_id=game_info["users"][username]["slack_id"])
                .in_thread(thread_id=game_info["parent_message_ts"])
                .build()
            )
    return game_info


def roll_dice(
    slack_client: WebClient, game_info: dict, message_id: str, username: str
) -> None:
    log.info("Action: Rolled Dice")
    slack_client.chat_update(
        **slack_api.producers.update_parent_message(
            game_info=game_info, state="started"
        )
    )
    slack_api.producers.delete_message(channel=game_info["channel"], ts=message_id)
    slack_api.producers.roll_with_player_message(
        slack_client=slack_client, game_info=game_info, username=username, steal=False
    )
    return None


def steal_dice(
    slack_client: WebClient, game_info: dict, message_id: str, username: str
) -> None:
    slack_api.producers.delete_message(channel=game_info["channel"], ts=message_id)
    slack_api.producers.roll_with_player_message(
        slack_client=slack_client, game_info=game_info, username=username, steal=True
    )
    return None


def start_game(
    slack_client: WebClient,
    game_info: dict,
    response_url: str,
    auto_break: bool = False,
) -> dict:
    if auto_break:
        game_info["auto_break"] = True
    else:
        game_info["auto_break"] = False
    start_response = dice10k.start_game(game_info["game_id"])
    turn_player = start_response["turn-player"]
    game_info["title_message_url"] = response_url
    slack_client.chat_update(
        **slack_api.producers.update_parent_message(
            game_info=game_info, state="started"
        )
    )
    slack_api.producers.roll_with_player_message(
        slack_client=slack_client, game_info=game_info, username=turn_player
    )

    return game_info
