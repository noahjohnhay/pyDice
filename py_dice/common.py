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


def who_can_steal(game_id: str, winning_threshold: int = 3000) -> list:
    players = dice10k.fetch_game(game_id)["players"]
    if len(players) > 1:
        previous_player = next(p for p in players if p["turn-order"] == 1)
    else:
        previous_player = players[0]
    matched_players = []
    for player in players:
        # log.info(
        #     f"{players} \n"
        #     f"{player} \n"
        #     f"{bool((previous_player['pending-points'] + player['points']) < winning_threshold)} \n"
        #     f"{player['ice-broken?']}\n"
        #     f"{is_robbable(game_id=game_id, username=previous_player['name'])}\n"
        #     f"{bool(previous_player['points'] >= 1000)}"
        # )
        if (
            # Total points won't put you over the winning threshold
            bool(
                (previous_player["pending-points"] + player["points"])
                < winning_threshold
            )
            # Current user broke the ice
            and player["ice-broken?"]
            # Previous player is robbable
            and is_robbable(game_id=game_id, username=previous_player["name"])
            # Verify current player has 1000 points
            and bool(previous_player["points"] >= 1000)
        ):
            matched_players.append(player["name"])
    log.info(matched_players)
    return matched_players


def is_game_over(game_id: str, winning_threshold: int = 3000) -> bool:
    players = dice10k.fetch_game(game_id).get("players", None)
    log.info(players)
    if players:
        # TODO: catch if no one stole, and also make sure you don't present roll button is someone is gonna win
        if not who_can_steal(game_id):
            for player in players:
                if player["points"] + player["pending-points"] == winning_threshold:
                    log.info(f"{player['name']} has won")
                    return True
                elif player["points"] + player["pending-points"] > winning_threshold:
                    log.exception(
                        f"{player['name']} has somehow surpassed the winning threshold"
                    )
    return False


def get_game_id(payload: dict) -> str:
    if is_valid_uuid(payload["actions"][0].get("block_id", "")):
        return payload["actions"][0]["block_id"]
    else:
        return payload["actions"][0]["value"]


def is_robbable(game_id: str, username: str) -> bool:
    # TODO: update to be checked once and maintained in state
    players = dice10k.fetch_game(game_id)["players"]
    player_info = next(p for p in players if p["name"] == username)
    if player_info["points"] >= 1000:
        return True
    else:
        return False
