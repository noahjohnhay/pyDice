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


def add_player(game_id: str, name: str) -> dict:
    print(game_id)
    print(name)
    response = requests.post(
        f"http://dice.calinfraser.com/games/{game_id}/players", json={"name": name}
    )
    print(f"response is: {response.status_code}: {response.content}")
    body = json.loads(response.content)
    return body


def roll(game_id: str, user_id: str) -> dict:
    response = requests.put(f"http://dice.calinfraser.com/games/{game_id}/players/{user_id}/roll")
    body = json.loads(response.content)
    print(f"response is: {response.status_code}: {body}")
    return body