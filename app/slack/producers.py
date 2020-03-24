import requests
import re
from functools import reduce


# roll = [1, 2, 3, 4, 4, 6]


def format_emojiis(x1: str, x2: int) -> str:
    """
    Description:
        Format slack emoji
    Args:
        x1: str -
        x2: int - die number
    Returns:
        str - Formatted slack emoji
    """
    return f'{x1} :die{x2}:'


# function for a reduce
def build_options(acc, x):
    acc.append({
        "text": {
            "type": "plain_text",
            "text": f':die{x}:'
        },
        "value": f'value-{len(acc) + 1}'
    })
    return acc


def fetch_die_val(acc, x):
    die = x["text"]["text"]
    acc.append(int(re.search(r'\d+', die).group()))
    return acc


def build_slack_message(roll_val, pronoun: str, pickable: bool, action: str = "rolled"):
    params = {
        "blocks": [
            {
                "type": "section",
                "block_id": "{gameId}-{rand_val}",
                "text": {
                    "type": "mrkdwn",
                    "text": "tobereplaced"
                }
            }
        ]}
    if pickable:
        params["blocks"][0]["accessory"] = {
            "action_id": "text1234",
            "type": "multi_static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Pick to keep"
            },
            "options": [
            ]
        }
        params["blocks"][0]["accessory"]["options"] = reduce(build_options, roll_val, [])
    params["blocks"][0]["text"]["text"] = f'{pronoun} {action}: {reduce(format_emojiis, roll_val, "")}'
    print(params)
    return params


def ask_for_players(game_requestor: str):
    params = ""
    send_requests()
    return


def respond_slash_command(params, username: str):
    roll = [1, 2, 3, 6]
    send_requests(build_slack_message(roll, f'@{username}', False))
    response = requests.post(params["response_url"], json=build_slack_message(roll, 'You', True))
    # print(response)
    return response


def send_picks(pick_list, username):
    roll = reduce(fetch_die_val, pick_list, [])
    params = build_slack_message(roll, f'@{username}', False, "picked")
    return send_requests(params)


def send_requests(params):
    response = requests.post("https://hooks.slack.com/services/*",
                             json=params)
    return response
