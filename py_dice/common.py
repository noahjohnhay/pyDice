import re
from functools import reduce


def format_dice_emojis(roll_val: list) -> str:
    return reduce(format_dice_emoji, roll_val, "")


def format_dice_emoji(x1: str, x2: int) -> str:
    return f"{x1} :die{x2}:"


def fetch_die_val(acc: list, x: dict) -> list:
    die = x["text"]["text"]
    acc.append(int(re.search(r"\d+", die).group()))
    return acc
