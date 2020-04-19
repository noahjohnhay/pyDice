# coding=utf-8

import json
from functools import reduce

from flask import Flask, Response, request
from logbook import Logger
from py_dice import common, dcs, dice10k, slack_api

log = Logger(__name__)


def start_api():
    game_state = {}
    flask_app = Flask(__name__)
    flask_app.config["DEBUG"] = True
    slack_client = slack_api.producers.create_client()

    @flask_app.route("/create", methods=["POST"])
    def create_game() -> Response:
        username = request.form["user_name"]
        game_id = dice10k.create_game()["game-id"]
        game_state[game_id] = {"game_id": game_id, "users": {}}
        game_state[game_id]["channel"] = request.form["channel_id"]
        response = slack_client.chat_postMessage(
            **dcs.message.create(
                game_id=game_id,
                channel_id=game_state[game_id]["channel"],
                message=f"@{username} started a game, click to join:",
            )
            .add_button(game_id=game_id, text="Join Game", action_id="join_game")
            .add_start_game(game_id=game_id)
            .add_start_game(game_id=game_id, auto_break=True)
            .build()
        )
        game_state[game_id]["parent_message_ts"] = response["ts"]
        return Response("", 200)

    @flask_app.route("/action", methods=["POST"])
    def action_route() -> Response:
        payload = json.loads(request.form["payload"])
        action = payload["actions"][0]["action_id"]
        delete_message_ts = payload["response_url"]
        game_id = common.get_game_id(payload)
        if common.is_game_over(game_id):
            # TODO: POST GAME OVER SUMMARY SEE OTHER TODO in update parent message
            resp = slack_api.producers.update_parent_message(
                game_info=game_state[game_id], state="completed"
            )
            log.info(resp)
            log.info("GAME OVER")
            return Response("", 200)
        elif action == "join_game":
            game_state[game_id]["message_ts"] = delete_message_ts
            game_state[game_id].update(
                slack_api.actions.join_game(
                    slack_client=slack_client,
                    game_info=game_state[game_id],
                    slack_user_id=payload["user"]["id"],
                    username=payload["user"]["username"],
                )
            )
            return Response("", 200)

        elif action == "pass_dice":
            slack_api.producers.update_parent_message(
                game_info=game_state[game_id], state="started"
            )
            slack_api.actions.pass_dice(
                slack_client=slack_client,
                game_info=game_state[game_id],
                message_id=delete_message_ts,
                username=payload["user"]["username"],
            )
            return Response("", 200)

        elif action == "pick_die":
            log.info("GAME STATE")
            log.info(game_state)
            game_state[game_id].update(
                slack_api.actions.pick_dice(
                    slack_client=slack_client,
                    game_info=game_state[game_id],
                    message_id=delete_message_ts,
                    username=payload["user"]["username"],
                    picks=reduce(
                        common.fetch_die_val,
                        payload["actions"][0]["selected_options"],
                        [],
                    ),
                )
            )
            return Response("", 200)

        elif action == "roll_dice":
            slack_api.producers.update_parent_message(
                game_info=game_state[game_id], state="started"
            )
            slack_api.actions.roll_dice(
                slack_client=slack_client,
                game_info=game_state[game_id],
                message_id=delete_message_ts,
                username=payload["user"]["username"],
            )
            return Response("", 200)

        elif action == "steal_dice":
            slack_client.chat_postMessage(
                **dcs.message.create(
                    game_id=game_state[game_id]["game_id"],
                    channel_id=game_state[game_id]["channel"],
                    message=f"{payload['user']['username']} is trying to steal",
                )
                .in_thread(game_state[game_id]["parent_message_ts"])
                .build()
            )
            slack_api.actions.steal_dice(
                slack_client=slack_client,
                game_info=game_state[game_id],
                message_id=delete_message_ts,
                username=payload["user"]["username"],
            )
            return Response("", 200)

        elif action == "start_game":
            game_state[game_id].update(
                slack_api.actions.start_game(
                    slack_client=slack_client,
                    game_info=game_state[game_id],
                    response_url=payload["response_url"],
                    auto_break=False,
                )
            )
            return Response("", 200)
        elif action == "start_game_auto":
            game_state[game_id].update(
                slack_api.actions.start_game(
                    slack_client=slack_client,
                    game_info=game_state[game_id],
                    response_url=payload["response_url"],
                    auto_break=True,
                )
            )
            return Response("", 200)

        else:
            log.warn("Action not recognized")
            return Response("", 404)

    @flask_app.route("/gamestate", methods=["POST"])
    def game_state_fn() -> Response:
        log.debug(f"Game State: {json.dumps(game_state, indent=2)}")
        return Response(game_state, 200)

    flask_app.run()
