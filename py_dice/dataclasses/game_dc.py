from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class Games:
    games: dict

    def build(self: Games) -> dict:
        return self.games

    def add_game(self: Games, game_id: str) -> Games:
        self.games[game_id] = {}
        return self

    def add_user(self: Games, game_id: str, user_id: str) -> Games:
        if "users" not in self.games[game_id]:
            self.games[game_id]["users"] = []
        self.games[game_id]["users"].append({"user_id": user_id})
        return self


def create() -> Games:
    games = {}
    return Games(games)
