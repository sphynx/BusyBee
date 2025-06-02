from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

import requests
from dotenv import load_dotenv
from requests.auth import AuthBase


class TokenAuth(AuthBase):
    """Implements a token authentication scheme for Lichess."""
    def __init__(self, token: Optional[str] = None):
        if token is None:
            token = os.getenv('LICHESS_TOKEN')

        self.token = token

    def __call__(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request


LICHESS_TOKEN = TokenAuth()

SLOW_THRESHOLD = 15

@dataclass(frozen=True)
class PlayingUser:
    name: str
    game_id: str
    starting_time: int
    increment: int

    @classmethod
    def from_lichess(cls, msg: dict[str, Any]) -> Optional[PlayingUser]:
        if msg.get('playing', False):
            name = msg.get('name', '')

            info = msg['playing']

            if not isinstance(info, dict):
                print(f"Didn't get the game data, just this: {msg}")

                # We can't determine the time control, so give up for this user:
                return None

            clock = info.get('clock', '')
            game_id = info.get('id', '')

            if '+' in clock:
                t, incr = clock.split('+')
                try:
                    t = int(t)
                    incr = int(incr)
                    return cls(name=name, game_id=game_id, starting_time=t, increment=incr)

                except Exception:
                    return None

    def total_time_minutes(self) -> float:
        return self.starting_time + (2/3) * self.increment

    @property
    def game_url(self) -> str:
        return f"https://lichess.org/{self.game_id}"

    @property
    def is_slower(self) -> bool:
        return self.total_time_minutes() >= SLOW_THRESHOLD

    @property
    def clock(self) -> str:
        return f"{self.starting_time}+{self.increment}"




class LichessUserChecker:
    def __init__(self, users: tuple[str, ...] = ()):
        self.token = TokenAuth()
        self.users = list(users)

    def check_slow_games(self) -> list[PlayingUser]:
        print(f"{datetime.now()}: checking {len(self.users)} users: {self.users}")

        url = f"https://lichess.org/api/users/status"

        if len(self.users) > 100:
            # Lichess only handles 100 users per query, it should be enough for us
            users = self.users[:100]
        else:
            users = self.users

        params = {
            'ids': ','.join(users),
            'withGameMetas': 'true',
        }

        statuses = requests.get(url, auth=self.token, params=params).json()

        res = []
        for s in statuses:
            playing_user = PlayingUser.from_lichess(s)
            if playing_user is not None and playing_user.is_slower:
                res.append(playing_user)

        return res


if __name__ == '__main__':
    users = ("sphynx", "arjunpyda", "jdannan", "e_rider", "sofaking83")

    load_dotenv()

    checker = LichessUserChecker(users)
    playing_users = checker.check_slow_games()

    if not playing_users:
        print("No one is playing")
    else:
        for u in playing_users:
            print(f"{u.name} is playing a slower game: {u.clock}, URL: {u.game_url}")
