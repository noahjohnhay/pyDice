# coding=utf-8

import json

import requests


def create_game() -> dict:
    response = requests.post("http://dice.calinfraser.com/games")
    body = json.loads(response.content)
    print(f"response is: {response.status_code}: {body}")
    return body


def fetch_game(game_id: str) -> dict:
    response = requests.get(f"http://dice.calinfraser.com/games/{game_id}")
    body = json.loads(response.content)
    print(f"response is: {response.status_code}: {body}")
    return body


def start_game(game_id: str) -> dict:
    response = requests.put(f"http://dice.calinfraser.com/games/{game_id}/start")
    body = json.loads(response.content)
    print(f"response is: {response.status_code}: {body}")
    return body


def add_player(game_id: str, name: str) -> str:
    response = requests.post(
        f"http://dice.calinfraser.com/games/{game_id}/players", json={"name": name}
    )
    body = json.loads(response.content)
    print(f"response is: {response.status_code}: {body}")
    return body["player-id"]
