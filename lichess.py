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


SLOW_THRESHOLD = 30

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
                print(f"Can't get time control from Lichess: {msg}")
                # We can't determine the time control, likely it's blitz, so give up for this user:
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

    def does_user_exist(self, user: str) -> bool:
        print(f"{datetime.now()}: checking existence of user '{user}' on Lichess")
        url = f"https://lichess.org/api/user/{user}"
        return requests.get(url, auth=self.token).ok

    def get_current_game(self, user: str) -> Optional[PlayingUser]:
        print(f"{datetime.now()}: getting current game of user '{user}'")
        url = f"https://lichess.org/api/user/{user}/current-game"
        params = {
            'moves': 'false',
            'evals': 'false',
            'opening': 'false',
            'clocks': 'false',
        }

        headers = {'Accept': 'application/json'}
        game_data = requests.get(url, auth=self.token, params=params, headers=headers).json()

        game_id = game_data.get("id")
        clock = game_data.get("clock")
        if clock is not None:
            start = int(clock.get("initial", 0) / 60)
            increment = clock.get("increment", 0)
        else:
            start = 0
            increment = 0

        status = game_data.get("status")

        if game_id is not None and status == "started":
            return PlayingUser(name=user, game_id=game_id, starting_time=start, increment=increment)
        else:
            return None

    def check_slow_games(self) -> list[PlayingUser]:
        print(f"{datetime.now()}: checking games of {len(self.users)} users on Lichess")

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
            # Check if we got the game metadata correctly:
            if "playing" in s and not isinstance(s["playing"], dict):
                # We didn't, so get the current game of the user
                playing_user = self.get_current_game(s.get('id'))
            else:
                playing_user = PlayingUser.from_lichess(s)

            if playing_user is not None and playing_user.is_slower:
                res.append(playing_user)

        return res


if __name__ == '__main__':
    users = ("sphynx", "jdannan", "e_rider")

    load_dotenv()

    checker = LichessUserChecker(users)
    playing_users = checker.check_slow_games()

    if not playing_users:
        print("No one is playing")
    else:
        for u in playing_users:
            print(f"{u.name} is playing a slower game: {u.clock}, URL: {u.game_url}")

    print(checker.get_current_game("sphynx"))
