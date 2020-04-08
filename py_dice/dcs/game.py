from __future__ import annotations

import dataclasses

from .user import User


@dataclasses.dataclass
class Game:
    game: dict

    def build(self: Game) -> dict:
        return self.game

    def add_user(self: Game, user: User, username: str) -> Game:
        self.game["users"][username] = user.build()
        return self


def create(game_id: str) -> Game:
    game = {"game_id": game_id, "users": {}}
    return Game(game)
