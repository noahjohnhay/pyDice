# coding=utf-8

import json

from flask import Flask, request
from py_dice import dice10k, slack


def start_api():
    game_state = {}
    flask_app = Flask(__name__)
    flask_app.config["DEBUG"] = True

    @flask_app.route("/create", methods=["POST"])
    def create_game():
        username = request.form["user_name"]
        game_info = dice10k.manage.create_game()
        game_id = game_info["game-id"]
        game_state[game_id] = {}
        slack.producers.join_game_survey(username, game_id)
        return f"Created game {game_id}"

    @flask_app.route("/roll", methods=["POST"])
    def roll_route():
        slack.producers.respond_slash_command(request.form, request.form["user_name"])
        return ""

    @flask_app.route("/action", methods=["POST"])
    def action_route():
        action = json.loads(request.form["payload"])["actions"][0]["action_id"]

        if action == "join_game":
            print(action)
        elif action == "pick_die":
            print(action)
            payload = json.loads(request.form["payload"])
            pick_list = payload["actions"][0]["selected_options"]
            slack.producers.send_picks(pick_list, payload["user"]["username"])
        return ""

    # test stuff
    @flask_app.route("/picknose", methods=["POST"])
    def pick_nose():
        print(game_state)
        game_state.update(request.json)
        return "nose was picked"

    @flask_app.route("/gamestate", methods=["POST"])
    def game_state_fn():
        print(game_state)
        return game_state

    @flask_app.route("/print", methods=["POST"])
    def print_response():
        print(json.dumps(json.loads(request.form["payload"]), indent=2))
        return "true"

    flask_app.run()
