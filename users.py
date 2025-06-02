from pathlib import Path
from typing import Optional

USERS_FILE = "data/users.csv"

class Users:
    def __init__(self):
        self.users = {}

        self.users_file = Path(USERS_FILE)

        if self.users_file.exists():
            for line in self.users_file.read_text().split("\n"):
                if line:
                    parts = line.split(",")

                    if len(parts) != 2:
                        raise ValueError("Unexpected line format, expected: LICHESS_USERNAME,DISCORD_ID")

                    lichess_username = parts[0]
                    discord_id = int(parts[1])

                    self.users[lichess_username] = discord_id

            print(f"Loaded {len(self.users)} users from DB")

    def add_user(self, lichess: str, discord_id: int) -> None:
        self.users[lichess] = discord_id
        self._append_user(lichess, discord_id)

    def discord_to_lichess(self, discord_id: int) -> Optional[str]:
        for k, v in self.users.items():
            if v == discord_id:
                return k
        return None

    def lichess_to_discord(self, lichess_username: str) -> Optional[int]:
        return self.users.get(lichess_username)

    def lichess_usernames(self) -> tuple[str, ...]:
        return tuple(sorted(self.users.keys()))

    def _append_user(self, lichess: str, discord_id: int) -> None:
        with self.users_file.open("a") as f:
            f.write(f"{lichess},{discord_id}\n")

    def dump_to_file(self) -> None:
        self.users_file.write_text("\n".join(
            f"{lichess},{discord}"
            for lichess, discord in self.users.items())
        )
