# coding=utf-8

from logbook import Logger
from py_dice import common, dice10k, slack_api
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
            "broken_int": 0,
        }
        slack_client.chat_postMessage(
            **slack_api.bodies.respond_in_thread(
                game_info=game_info,
                message=f"@{username} has successfully joined the game",
            )
        )
    return game_info


def pass_dice(
    slack_client: WebClient, game_info: dict, message_id: str, username: str
) -> None:
    log.info("Action: Pass Dice")
    slack_api.producers.delete_message(channel=game_info["channel"], ts=message_id)
    response = dice10k.pass_turn(
        game_id=game_info["game_id"], user_id=game_info["users"][username]["user_id"]
    )
    turn_player = response["game-state"]["turn-player"]
    steal_able = False
    for x in response["game-state"]["players"]:
        if (
            x["name"] == turn_player
            and x["ice-broken?"]
            and game_info["users"][username]["broken_int"] > 1
        ):
            steal_able = True
    if steal_able:
        log.warn("Trigger steal message")
        slack_client.chat_postEphemeral(
            **slack_api.bodies.steal_roll_survey(
                game_info=game_info, username=response["game-state"]["turn-player"]
            )
        )
    else:
        slack_api.producers.roll_with_player_message(
            slack_client=slack_client, game_info=game_info, username=turn_player
        )
    slack_client.chat_update(
        **slack_api.bodies.update_parent_message(game_info=game_info)
    )
    return None


def pick_dice(
    slack_client: WebClient, game_info: dict, message_id: str, username: str, picks: list
):
    log.debug("Action: Picked Dice")
    response = dice10k.send_keepers(
        game_id=game_info["game_id"], user_id=game_info["users"][username]["user_id"], picks=picks
    )
    ice_broken = False
    for x in response["game-state"]["players"]:
        if x["name"] == username:
            log.info("found ice state")
            ice_broken = x["ice-broken?"]
            break
    if response["message"] == "Must pick at least one scoring die":
        slack_client.chat_postMessage(
            **slack_api.bodies.build_slack_message(
                roll_val=response["roll"],
                message=f"{response['message']}, try again: {common.format_dice_emojis(response['roll'])}",
                pickable=True,
                game_info=game_info,
                username=username,
            )
        )
    else:
        slack_api.producers.delete_message(
            channel=game_info["channel"], ts=message_id
        )
        slack_client.chat_postMessage(
            **slack_api.bodies.respond_in_thread(
                game_info=game_info,
                message=f"@{username}\n"
                f"Picked: {common.format_dice_emojis(picks)}\n"
                f"Pending Points: {response['pending-points']}\n"
                f"Remaining Dice: {response['game-state']['pending-dice']}\n",
            )
        )

        if not (ice_broken or response.get("pending-points", 0) >= 1000):
            roll_dice(
                slack_client=slack_client,
                game_info=game_info,
                message_id=message_id,
                username=username,
            )
        else:
            game_info["users"][username]["broken_int"] += 1
            slack_client.chat_postEphemeral(
                **slack_api.bodies.pass_roll_survey(
                    game_info=game_info, username=username, can_pass=True
                )
            )
    return game_info


def roll_dice(
    slack_client: WebClient, game_info: dict, message_id: str, username: str
) -> None:
    log.info("Action: Rolled Dice")
    slack_client.chat_update(
        **slack_api.bodies.update_parent_message(game_info=game_info)
    )
    slack_api.producers.delete_message(channel=game_info["channel"], ts=message_id)
    slack_api.producers.roll_with_player_message(
        slack_client=slack_client, game_info=game_info, username=username
    )
    return None


def steal_dice(
    slack_client: WebClient, game_info: dict, message_id: str, username: str
) -> None:
    slack_api.producers.delete_message(channel=game_info["channel"], ts=message_id)
    # TODO fix this you fuck
    # requests.post(url=response_url, json={"delete_original": True})
    slack_api.producers.roll_with_player_message(
        slack_client=slack_client, game_info=game_info, username=username, steal=True
    )
    return None


def start_game(slack_client: WebClient, game_info: dict, response_url: str) -> dict:
    start_response = dice10k.start_game(game_info["game_id"])
    turn_player = start_response["turn-player"]
    game_info["title_message_url"] = response_url
    slack_client.chat_update(
        **slack_api.bodies.update_parent_message(game_info=game_info)
    )
    slack_api.producers.roll_with_player_message(
        slack_client=slack_client, game_info=game_info, username=turn_player
    )
    return game_info
