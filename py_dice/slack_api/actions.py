# coding=utf-8

import json
import os

import slack
from logbook import Logger
from py_dice import common, dice10k, slack_api

log = Logger(__name__)

slack_token = os.environ["SLACK_API_TOKEN"]
client = slack.WebClient(token=slack_token)
log.debug("STARTING THE CLIENT AGAIN")


def join_game(game_info: dict, slack_user_id: str, username: str) -> dict:
    if username not in game_info["users"]:
        game_info["users"][username] = {
            "user_id": dice10k.add_player(game_info["game_id"], username)["player-id"],
            "slack_id": slack_user_id,
            "broken_int": 0,
        }
        client.chat_postMessage(
            **slack_api.bodies.respond_in_thread(
                game_info, f"@{username} has successfully joined the game"
            )
        )

    return game_info


def pass_dice(game_info: dict, message_id: str, username: str) -> None:

    log.warn("Action: Pass Dice")
    log.warn(message_id)
    slack_api.producers.delete_message(channel=game_info["channel"], ts=message_id)
    response = dice10k.pass_turn(
        game_id=game_info["game_id"], user_id=game_info["users"][username]["user_id"]
    )
    log.warn(response)
    turn_player = response["game-state"]["turn-player"]
    steal_able = False
    log.warn(game_info)
    for x in response["game-state"]["players"]:
        if (
            x["name"] == turn_player
            and x["ice-broken?"]
            and game_info["users"][username]["broken_int"] > 1
        ):
            steal_able = True
    if steal_able:
        log.warn("Trigger steal message")
        client.chat_postEphemeral(
            **slack_api.bodies.steal_roll_survey(
                game_info, response["game-state"]["turn-player"]
            )
        )
    else:
        log.warn(response)
        slack_api.producers.roll_with_player_message(game_info, turn_player)
    client.chat_update(**slack_api.bodies.update_parent_message(game_info))
    return None


def pick_dice(game_info: dict, message_id: str, username: str, roll: list):
    log.debug("Action: Picked Dice")
    response = dice10k.send_keepers(
        game_info["game_id"], game_info["users"][username]["user_id"], roll
    )
    ice_broken = False
    for x in response["game-state"]["players"]:
        log.info(x)
        if x["name"] == username:
            log.info("found ice state")
            ice_broken = x["ice-broken?"]
            break
    if response["message"] == "Must pick at least one scoring die":
        client.chat_postMessage(
            **slack_api.bodies.build_slack_message(
                response["roll"],
                f'{response["message"]}, try again: {common.format_dice_emojis(response["roll"])}',
                True,
                game_info,
                username,
            )
        )
    else:
        try:
            slack_api.producers.delete_message(
                channel=game_info["channel"], ts=message_id
            )
        except Exception as e:
            log.warn(e)
        formated_roll = common.format_dice_emojis(roll)
        client.chat_postMessage(
            **slack_api.bodies.respond_in_thread(
                game_info,
                f"@{username}\n"
                f"Picked: {formated_roll}\n"
                f"Pending Points: {response['pending-points']}\n"
                f"Remaining Dice: {response['game-state']['pending-dice']}\n",
            )
        )

        if not (ice_broken or response.get("pending-points", 0) >= 1000):
            roll_dice(game_info=game_info, message_id=message_id, username=username)
        else:
            game_info["users"][username]["broken_int"] += 1
            client.chat_postEphemeral(
                **slack_api.bodies.pass_roll_survey(
                    game_info=game_info,
                    username=username,
                    response=response,
                    ice_broken=ice_broken,
                )
            )
    return game_info


def roll_dice(game_info: dict, message_id: str, username: str) -> None:
    log.debug("Action: Rolled Dice")
    client.chat_update(**slack_api.bodies.update_parent_message(game_info))
    log.warn(message_id)
    try:
        slack_api.producers.delete_message(channel=game_info["channel"], ts=message_id)
    except Exception as e:
        log.warn(e)
    slack_api.producers.roll_with_player_message(game_info=game_info, username=username)
    return None


def steal_dice(game_info: dict, message_id: str, username: str) -> None:
    log.warn("function does nothing yet")
    slack_api.producers.delete_message(channel=game_info["channel"], ts=message_id)
    # TODO fix this you fuck
    # requests.post(url=response_url, json={"delete_original": True})
    steal_response = slack_api.producers.roll_with_player_message(
        game_info=game_info, username=username, steal=True
    )
    log.warn(steal_response)
    return steal_response


def start_game(game_info: dict, response_url: str):
    log.debug("Action: Started Game")
    start_response = dice10k.start_game(game_info["game_id"])
    turn_player = start_response["turn-player"]
    log.debug(f"Its this players turn: {turn_player}")
    log.debug(f"Start game response: {json.dumps(start_response, indent=2)}")
    game_info["title_message_url"] = response_url
    response = client.chat_update(
        **slack_api.bodies.update_parent_message(game_info=game_info)
    )
    log.warn(response)
    slack_api.producers.roll_with_player_message(game_info, turn_player)
    return game_info
