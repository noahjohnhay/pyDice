# coding=utf-8

import json

import requests
from flask import Flask, Response, request
from logbook import Logger
from py_dice import dice10k, slack_api

log = Logger(__name__)


def start_api():
    game_state = {}
    flask_app = Flask(__name__)
    flask_app.config["DEBUG"] = True

    @flask_app.route("/create", methods=["POST"])
    def create_game() -> Response:
        username = request.form["user_name"]
        game_id = dice10k.manage.create_game()["game-id"]
        game_state[game_id] = {"game_id": game_id, "users": {}}
        slack_api.producers.join_game_survey(username, game_id)
        return Response("", 200)

    @flask_app.route("/action", methods=["POST"])
    def action_route() -> Response:
        payload = json.loads(request.form["payload"])
        log.debug(json.dumps(payload, indent=2))
        action = payload["actions"][0]["action_id"]

        if action == "join_game":
            game_id = payload["actions"][0]["value"]
            log.debug(game_state)
            game_state[game_id]["channel"] = payload["channel"]["id"]
            game_state[game_id]["message_ts"] = payload["message"]["ts"]
            # TODO: check to make sure this does not fuck state
            game_state.update(slack_api.actions.join_game(game_state, payload))
            log.debug(json.dumps(game_state, indent=2))
            return Response("", 200)
        elif action == "pass_dice":
            requests.post(payload["response_url"], json={"delete_original": True})
            game_id = payload["actions"][0]["value"]
            slack_api.actions.pass_dice(
                game_state[game_id], payload["user"]["username"]
            )
            return Response("", 200)
        elif action == "pick_die":
            game_id = payload["actions"][0]["block_id"]
            log.debug(game_state)
            slack_api.actions.pick_dice(payload, game_state[game_id])
            return Response("", 200)
        elif action == "roll_dice":
            requests.post(payload["response_url"], json={"delete_original": True})
            game_id = payload["actions"][0]["value"]
            slack_api.actions.roll_dice(
                game_state[game_id], payload["user"]["username"]
            )
            return Response("", 200)
        elif action == "start_game":
            game_id = payload["actions"][0]["value"]
            slack_api.actions.start_game(payload, game_state[game_id])
            return Response("", 200)
        else:
            log.error("Action not recognized")
            return Response("", 404)

    @flask_app.route("/gamestate", methods=["POST"])
    def game_state_fn() -> Response:
        log.debug(f"Game sate: {json.dumps(game_state, indent=2)}")
        return Response("", 200)

    flask_app.run()
