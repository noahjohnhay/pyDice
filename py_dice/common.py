import re
from functools import reduce
from uuid import UUID

from logbook import Logger
from py_dice import dice10k

log = Logger(__name__)


def format_dice_emojis(roll_val: list) -> str:
    return reduce(format_dice_emoji, roll_val, "")


def format_dice_emoji(x1: str, x2: int) -> str:
    return f"{x1} :die{x2}:"


def fetch_die_val(acc: list, x: dict) -> list:
    die = x["text"]["text"]
    acc.append(int(re.search(r"\d+", die).group()))
    return acc


def is_valid_uuid(uuid_to_test: str, version: int = 4) -> bool:
    try:
        UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return True


def is_ice_broken():
    return


def can_steal(game_info: dict, winning_threshold: int = 3000) -> bool:
    players = dice10k.fetch_game(game_info["game_id"])["players"]
    current_player = next(p for p in players if p["turn-order"] == 0)
    current_points = current_player["points"]
    ice_broken = current_player["ice-broken?"]
    log.info(players)
    previous_player = next(p for p in players if p["turn-order"] == 1)
    if len(players) > 1:
        # If there is more than one player use previous players pending points
        pending_points = previous_player["pending-points"]
    else:
        # Else use your own pendings points
        pending_points = current_player["pending-points"]
    log.info(
        f"current player {current_player}\n"
        f"previous player {previous_player}\n"
        f"{bool((pending_points + current_points) < winning_threshold)}\n"
        f"{ice_broken}\n"
        f"{game_info['users'][previous_player['name']]['robbable']}\n"
        f"previous player points {bool(previous_player['points'] > 1000)}"
    )
    if (
        # Total points won't put you over the winning threshold
        bool((pending_points + current_points) < winning_threshold)
        # Current user broke the ice
        # TODO and 1 not 0 or 2
        # Previous player is robbable
        and game_info["users"][previous_player["name"]]["robbable"]
        # Verify cuurent player has 1000 points
        and bool(previous_player["points"] >= 1000)
    ):
        return True
    return False


def is_game_over(game_id: str, winning_threshold: int = 3000) -> bool:
    players = dice10k.fetch_game(game_id)["players"]
    for player in players:
        if player["points"] == winning_threshold:
            log.info(f"{player['name']} has won")
            return True
        elif player["points"] >= winning_threshold:
            log.exception(
                f"{player['name']} has somehow surpassed the winning threshold"
            )
    return False


def get_game_id(payload: dict) -> str:
    if is_valid_uuid(payload["actions"][0].get("block_id", "")):
        return payload["actions"][0]["block_id"]
    else:
        return payload["actions"][0]["value"]
