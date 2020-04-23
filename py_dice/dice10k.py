# coding=utf-8

import json

import requests
from logbook import Logger

log = Logger(__name__)


def create_game() -> dict:
    response = json.loads(requests.post("http://localhost:3000/games").content)
    log.info(f"Create game response: {json.dumps(response, indent=2)}")
    return response


def fetch_game(game_id: str) -> dict:
    response = json.loads(
        requests.get(f"http://localhost:3000/games/{game_id}").content
    )
    log.info(f"Fetch game response: {json.dumps(response, indent=2)}")
    return response


def start_game(game_id: str) -> dict:
    response = json.loads(
        requests.put(f"http://localhost:3000/games/{game_id}/start").content
    )
    log.info(f"Start game response: {json.dumps(response, indent=2)}")
    return response


def add_player(game_id: str, name: str) -> dict:
    response = json.loads(
        requests.post(
            f"http://localhost:3000/games/{game_id}/players", json={"name": name}
        ).content
    )
    log.info(f"Add player response: {response}")
    return response


def roll(game_id: str, user_id: str, steal: bool) -> dict:
    if steal:
        payload = {"steal": True}
    else:
        payload = {}
    response = json.loads(
        requests.post(
            f"http://localhost:3000/games/{game_id}/players/{user_id}/roll",
            json=payload,
        ).content
    )
    log.info(f"Roll response: {response}")
    return response


def send_keepers(game_id: str, user_id: str, picks: list) -> dict:
    log.info(f"Send Keepers {game_id} {user_id} {picks}")
    response = json.loads(
        requests.post(
            f"http://localhost:3000/games/{game_id}/players/{user_id}/keep",
            json={"keepers": picks},
        ).content
    )
    log.info(f"Keep response: {response}")
    return response


def pass_turn(game_id: str, user_id: str) -> dict:
    response = json.loads(
        requests.post(
            f"http://localhost:3000/games/{game_id}/players/{user_id}/pass"
        ).content
    )
    log.info(f"Pass response: {response}")
    return response
