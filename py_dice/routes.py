# coding=utf-8

import json

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
        game_id = dice10k.create_game()["game-id"]
        game_state[game_id] = {"game_id": game_id, "users": {}}
        slack_api.producers.join_game_survey(game_id=game_id, username=username)
        return Response("", 200)

    @flask_app.route("/action", methods=["POST"])
    def action_route() -> Response:
        payload = json.loads(request.form["payload"])
        action = payload["actions"][0]["action_id"]

        if action == "join_game":
            game_id = payload["actions"][0]["value"]
            game_state[game_id]["channel"] = payload["channel"]["id"]
            game_state[game_id]["message_ts"] = payload["message"]["ts"]
            game_state[game_id].update(
                slack_api.actions.join_game(
                    game_info=game_state[game_id], payload=payload
                )
            )
            return Response("", 200)

        elif action == "pass_dice":
            slack_api.actions.pass_dice(
                game_info=game_state[payload["actions"][0]["value"]],
                response_url=payload["response_url"],
                username=payload["user"]["username"],
            )
            return Response("", 200)

        elif action == "pick_die":
            slack_api.actions.pick_dice(
                game_info=game_state[payload["actions"][0]["block_id"]],
                response_url=payload["response_url"],
                username=payload["user"]["username"],
                payload=payload,
            )
            return Response("", 200)

        elif action == "roll_dice":
            slack_api.actions.roll_dice(
                game_info=game_state[payload["actions"][0]["value"]],
                response_url=payload["response_url"],
                username=payload["user"]["username"],
            )
            return Response("", 200)

        elif action == "start_game":
            game_id = payload["actions"][0]["value"]
            game_state[game_id].update(
                slack_api.actions.start_game(
                    game_info=game_state[game_id], response_url=payload["response_url"]
                )
            )
            return Response("", 200)

        else:
            log.error("Action not recognized")
            return Response("", 404)

    @flask_app.route("/gamestate", methods=["POST"])
    def game_state_fn() -> Response:
        log.debug(f"Game sate: {json.dumps(game_state, indent=2)}")
        return Response("", 200)

    flask_app.run()
