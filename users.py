from pathlib import Path
from typing import Optional

USERS_FILE = "data/users.csv"

class Users:
    def __init__(self):
        # lichess -> discord_id (optional because we may want just to follow arbitrary lichess users)
        self.users: dict[str, Optional[int]] = {}

        self.users_file = Path(USERS_FILE)

        if self.users_file.exists():
            for line in self.users_file.read_text().split("\n"):
                if line:
                    parts = line.split(",")

                    if len(parts) != 2:
                        raise ValueError("Unexpected line format, expected: LICHESS_USERNAME,DISCORD_ID")

                    lichess_username = parts[0]
                    discord_id = None if parts == "" else int(parts[1])

                    self.users[lichess_username] = discord_id

            print(f"Loaded {len(self.users)} users from DB")

    def add_user(self, lichess: str, discord_id: Optional[int]) -> bool:
        if lichess in self.users:
            return False
        else:
            self.users[lichess] = discord_id
            self._append_user(lichess, discord_id)
            return True

    def discord_to_lichess(self, discord_id: int) -> Optional[str]:
        for k, v in self.users.items():
            if v == discord_id:
                return k
        return None

    def lichess_to_discord(self, lichess_username: str) -> Optional[int]:
        return self.users.get(lichess_username)

    def lichess_usernames(self) -> tuple[str, ...]:
        return tuple(sorted(self.users.keys()))

    def _append_user(self, lichess: str, discord_id: Optional[int]) -> None:
        with self.users_file.open("a") as f:
            f.write(f"{lichess},{'' if discord_id is None else discord_id}\n")

    def dump_to_file(self) -> None:
        self.users_file.write_text("\n".join(
            f"{lichess},{'' if discord is None else discord}"
            for lichess, discord in self.users.items())
        )
