# coding=utf-8

import json

from flask import Flask, request
from py_dice import dice10k, slack
import requests



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


# JON DONT WRITE CODE ABOVE HERE
def start_api():
    game_state = {}
    flask_app = Flask(__name__)
    flask_app.config["DEBUG"] = True

    @flask_app.route("/create", methods=["POST"])
    def create_game():
        username = request.form["user_name"]
        game_info = dice10k.manage.create_game()
        game_id = game_info["game-id"]
        game_state[game_id] = {
            "users": {}
        }
        slack.producers.join_game_survey(username, game_id)
        return ""

    @flask_app.route("/roll", methods=["POST"])
    def roll_route():
        print(json.dumps(request.form))
        slack.producers.respond_slash_command(request.form, request.form["user_name"])
        return ""

    @flask_app.route("/action", methods=["POST"])
    def action_route():
        action = json.loads(request.form["payload"])['actions'][0]["action_id"]
        payload = json.loads(request.form["payload"])
        user = payload['user']["username"]
        if action == "join_game":
            game_id = payload['actions'][0]["value"]
            if user not in game_state[game_id]["users"]:
                response = dice10k.manage.add_player(game_id, user)
                game_state[game_id]["users"][user] = {"user_id": response["player-id"]}
                slack.producers.send_requests(slack.producers.build_join_response(user))
            print(f'game state: {game_state}')
            return ""
        elif action == "start_game":
            print("start game")
            response = dice10k.manage.start_game(payload['actions'][0]["value"])
            print(response)
            requests.post(payload["response_url"], json={
                "replace_original": "true",
                "text": "Game Has Been Started, hope Calin Joined :)"
            })
        # message suer to roll
            return ""
        elif action == "roll_dice":
            print("rolled")
            return ""
        elif action == "pick_die":
            pick_list = payload["actions"][0]["selected_options"]
            # delete message from response url
            requests.post(payload["response_url"], json={"delete_original":True})
            slack.producers.send_picks(pick_list, payload["user"]["username"])
            return ""
        elif action == "pass_dice":
            print("passed")
            return ""
        else:
            raise Exception("BADBADBADBAD")

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

