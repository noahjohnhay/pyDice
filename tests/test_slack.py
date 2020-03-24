from py_dice.slack import producers

goodOptions = {
    "blocks": [
        {
            "type": "section",
            "block_id": "section678",
            "text": {
                "type": "mrkdwn",
                "text": "You rolled:  :die1: :die2: :die3: :die4: :die4: :die6:",
            },
            "accessory": {
                "action_id": "text1234",
                "type": "multi_static_select",
                "placeholder": {"type": "plain_text", "text": "Pick to keep"},
                "options": [
                    {
                        "text": {"type": "plain_text", "text": ":die1:"},
                        "value": "value-1",
                    },
                    {
                        "text": {"type": "plain_text", "text": ":die2:"},
                        "value": "value-2",
                    },
                    {
                        "text": {"type": "plain_text", "text": ":die3:"},
                        "value": "value-3",
                    },
                    {
                        "text": {"type": "plain_text", "text": ":die4:"},
                        "value": "value-4",
                    },
                    {
                        "text": {"type": "plain_text", "text": ":die4:"},
                        "value": "value-5",
                    },
                    {
                        "text": {"type": "plain_text", "text": ":die6:"},
                        "value": "value-6",
                    },
                ],
            },
        }
    ]
}


def test_matchers():
    assert producers.build_slack_message([1, 2, 3, 4, 4, 6], "You", True) == goodOptions
