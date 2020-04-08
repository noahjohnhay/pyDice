from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class User:
    user: dict

    def build(self: User) -> dict:
        return self.user

    def update_broken_int(self: User, broken_int: int) -> User:
        self.user["broken_int"] = broken_int
        return self


def create(user_id: str, slack_id: str) -> User:
    user = {"user_id": user_id, "slack_id": slack_id, "broken_int": 0}
    return User(user)
