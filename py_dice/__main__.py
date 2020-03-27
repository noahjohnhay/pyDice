# coding=utf-8

from py_dice.dice_api import routes
from pydblite import Base

if __name__ == "__main__":
    db = Base("main.pdl")
    db.create("game_id", mode="override")
    routes.start_api()
