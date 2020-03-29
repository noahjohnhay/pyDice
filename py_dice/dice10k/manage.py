# coding=utf-8

import json

import requests
from logbook import Logger

log = Logger(__name__)


def create_game() -> dict:
    response = json.loads(requests.post("http://dice.calinfraser.com/games").content)
    log.debug(f"Create game response: {json.dumps(response, indent=2)}")
    return response


def fetch_game(game_id: str) -> dict:
    response = json.loads(
        requests.get(f"http://dice.calinfraser.com/games/{game_id}").content
    )
    log.debug(f"Fetch game response: {json.dumps(response, indent=2)}")
    return response


def start_game(game_id: str) -> dict:
    response = json.loads(
        requests.put(f"http://dice.calinfraser.com/games/{game_id}/start").content
    )
    log.debug(f"Start game response: {json.dumps(response, indent=2)}")
    return response


def add_player(game_id: str, name: str) -> dict:
    response = json.loads(
        requests.post(
            f"http://dice.calinfraser.com/games/{game_id}/players", json={"name": name}
        ).content
    )
    log.debug(f"Add player response: {response}")
    return response


def roll(game_id: str, user_id: str) -> dict:
    response = json.loads(
        requests.post(
            f"http://dice.calinfraser.com/games/{game_id}/players/{user_id}/roll"
        ).content
    )
    log.debug(f"Roll response: {response}")
    return response


def send_keepers(game_id: str, user_id: str, picks: list) -> dict:
    log.debug(f"{game_id} {user_id} {picks}")
    response = json.loads(
        requests.post(
            f"http://dice.calinfraser.com/games/{game_id}/players/{user_id}/keep",
            json={"keepers": picks},
        ).content
    )
    log.debug(f"keep response: {response}")
    return response


def pass_turn(game_id: str, user_id: str) -> dict:
    response = json.loads(
        requests.post(
            f"http://dice.calinfraser.com/games/{game_id}/players/{user_id}/pass"
        ).content
    )
    log.debug(f"pass response: {response}")
    return response
