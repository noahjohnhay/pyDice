# coding=utf-8

import json

from flask import Flask, Response, request
from logbook import Logger
from py_dice import dice10k, slack

log = Logger(__name__)


def start_api():
    game_state = {}
    flask_app = Flask(__name__)
    flask_app.config["DEBUG"] = True

    @flask_app.route("/create", methods=["POST"])
    def create_game() -> Response:
        username = request.form["user_name"]
        game_id = dice10k.manage.create_game()["game-id"]
        game_state[game_id] = {"users": {}}
        slack.producers.join_game_survey(username, game_id)
        return Response("", 200)

    @flask_app.route("/roll", methods=["POST"])
    def roll_route() -> Response:
        log.debug(f"Roll response: {json.dumps(request.form, indent=2)}")
        slack.producers.respond_slash_command(request.form, request.form["user_name"])
        return Response("", 200)

    @flask_app.route("/action", methods=["POST"])
    def action_route() -> Response:
        payload = json.loads(request.form["payload"])
        action = payload["actions"][0]["action_id"]
        user = payload["user"]["username"]

        if action == "join_game":
            slack.actions.join_game(game_state, payload, user)
            return Response("", 200)
        elif action == "pass_dice":
            slack.actions.pass_dice()
            return Response("", 200)
        elif action == "pick_die":
            slack.actions.pick_dice(payload)
            return Response("", 200)
        elif action == "roll_dice":
            slack.actions.role_dice()
            return Response("", 200)
        elif action == "start_game":
            slack.actions.start_game(payload)
            return Response("", 200)
        else:
            log.error("Action not recognized")
            return Response("", 404)

    @flask_app.route("/gamestate", methods=["POST"])
    def game_state_fn() -> Response:
        log.info(f"Game sate: {json.dumps(game_state, indent=2)}")
        return Response("", 200)

    flask_app.run()
