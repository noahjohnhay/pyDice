from py_dice.dataclasses import message


def build_slack_message(
    roll_val: list, text: str, pickable: bool, game_info: dict, username: str
) -> dict:
    body = (
        message.create(game_info["game_id"], game_info["channel"], text)
        .in_thread(game_info["message_ts"])
        .add_user(game_info["users"][username]["slack_id"])
    )
    if pickable:
        body.pick_die(roll_val)
    return body.build()


def respond_in_thread(game_info: dict, text: str) -> dict:
    body = message.create(game_info["game_id"], game_info["channel"], text).in_thread(
        game_info["message_ts"]
    )
    return body.build()


def pass_roll_survey(game_info: dict, username: str, response: dict, ice_broken: bool):
    body = (
        message.create(
            game_info["game_id"],
            game_info["channel"],
            f"@{username} would you like to roll or pass",
        )
        .add_button("roll_dice", "Roll")
        .in_thread(game_info["message_ts"])
        .add_user(game_info["users"][username]["slack_id"])
    )
    if ice_broken or response.get("pending-points", 0) >= 1000:
        body.add_button("pass_dice", "Pass")
    return body.build()


def join_game_survey(game_id: str, username: str) -> dict:
    body = (
        message.create(game_id, "", f"@{username} started a game, click to join:")
        .add_button("join_game", "Join Game")
        .add_start_game(game_id)
    )
    return body.build()
