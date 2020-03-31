from __future__ import annotations

import dataclasses
from functools import reduce


@dataclasses.dataclass
class Message:
    message: dict

    def build(self: Message) -> dict:
        return self.message

    def in_thread(self: Message, thread_id: str) -> Message:
        self.message["message_ts"] = thread_id
        return self

    def pick_die(self: Message, roll_val: list) -> Message:
        self.message["blocks"][0]["accessory"] = {
            "action_id": "pick_die",
            "type": "multi_static_select",
            "placeholder": {"type": "plain_text", "text": "Pick to keep"},
            "options": reduce(build_options, roll_val, []),
        }
        return self

    def add_user(self: Message, user_id: str) -> Message:
        self.message["user"] = user_id
        return self

    def add_start_game(self: Message, game_id: str) -> Message:
        self.message["blocks"][1]["elements"].append(
            {
                "type": "button",
                "action_id": "start_game",
                "text": {"type": "plain_text", "text": "Start Game"},
                "style": "danger",
                "confirm": {
                    "title": {"type": "plain_text", "text": "Are You Sure?"},
                    "text": {"type": "mrkdwn", "text": "Has everyone joined the game?"},
                    "confirm": {"type": "plain_text", "text": "Start Game!"},
                    "deny": {"type": "plain_text", "text": "Cancel"},
                },
                "value": game_id,
            }
        )
        return self

    def add_button(self: Message, button_id: str, text: str) -> Message:
        has_action = False
        button = {
            "type": "button",
            "action_id": button_id,
            "text": {"type": "plain_text", "text": text},
        }
        for idx, block in enumerate(self.message["blocks"]):
            if block["type"] == "actions":
                self.message["blocks"][idx]["elements"].append(button)
                has_action = True

        if not has_action:
            self.message["blocks"].append({"type": "actions", "elements": [button]})
        return self


def create(game_id: str, channel_id: str, message: str) -> Message:
    message = {
        "blocks": [
            {
                "type": "section",
                "block_id": game_id,
                "text": {"type": "mrkdwn", "text": message},
            }
        ],
        "channel": channel_id,
    }
    return Message(message)


def build_options(options: list, die_number: int) -> list:
    options.append(
        {
            "text": {"type": "plain_text", "text": f":die{die_number}:"},
            "value": f"value-{len(options) + 1}",
        }
    )
    return options
