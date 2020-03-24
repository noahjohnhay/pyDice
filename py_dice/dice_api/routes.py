# coding=utf-8

import json

from flask import Flask, request
from py_dice import dice10k, slack
from pydblite import Base


"""
{
   "token": "*",
   "team_id": "TC58SJX1P",
   "team_domain": "beefers",
   "channel_id": "C0107KZFHEV",
   "channel_name": "spammyshit",
   "user_id": "ddfd",
   "user_name": "jonathan.armel.daigle",
   "command": "/roll",
   "text": "",
   "response_url": "https://hooks.slack.com/commands/*",
   "trigger_id": ""
}
"""


def start_api():
    db = Base("main.pd1")
    flask_app = Flask(__name__)
    flask_app.config["DEBUG"] = True
    flask_app.run()

    @flask_app.route("/roll", methods=["POST"])
    def roll_route():
        print(json.dumps(request.form))
        slack.producers.respond_slash_command(request.form, request.form["user_name"])
        return "Logged."

    @flask_app.route("/pick", methods=["POST"])
    def pick_route():
        print("")
        payload = json.loads(request.form["payload"])
        pick_list = payload["actions"][0]["selected_options"]
        slack.producers.send_picks(pick_list, payload["user"]["username"])
        return "Logged."

    @flask_app.route("/create", methods=["POST"])
    def create_game():
        if db.exists():
            db.open()
        game_info = dice10k.manage.create_game()
        game_id = game_info["game-id"]
        print(db.insert(game_id=game_id))
        db.commit()
        for r in db:
            print(r)
        # slack.producers.ask_for_players(request.form["user_name"])
        return "dicks"

    @flask_app.route("/picknose", methods=["POST"])
    def pick_nose():
        return "nose was picked"
