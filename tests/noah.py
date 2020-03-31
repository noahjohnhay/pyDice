import json
import os

from py_dice.dataclasses import message

os.environ["SLACK_API_TOKEN"] = "test"

print("============================================")
print("BASIC MESSAGE")
print("============================================")

basic_message = message.create("game_id", "channel_id", "test_message")

print(json.dumps(basic_message.build(), indent=2))

print("============================================")
print("THREAD MESSAGE")
print("============================================")

thread_message = basic_message.in_thread("thread_id")

print(json.dumps(thread_message.build(), indent=2))

print("============================================")
print("ONE BUTTON")
print("============================================")

button_message = message.create("game_id", "channel_id", "test_message")

button_message.add_button("button_id", "button_text")

print(json.dumps(button_message.build(), indent=2))

print("============================================")
print("TWO BUTTONS")
print("============================================")

button_message.add_button("button_id_2", "button_text")

print(json.dumps(button_message.build(), indent=2))

print("============================================")

print("============================================")
