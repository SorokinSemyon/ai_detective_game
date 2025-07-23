import json
import os
from dataclasses import dataclass, asdict

from entites.game_entites.game_start import GameStart, Character


@dataclass
class UserInfo:
    username: str
    character: str

    @classmethod
    def from_json(cls, json_data):
        username = json_data["username"]
        character = json_data["character"]
        return cls(username, character)


@dataclass
class GameState:
    creator_username: str
    num_players: int
    setting: str
    game_start: GameStart
    users: dict[str, UserInfo]

    @classmethod
    def from_json(cls, json_data):
        creator_username = json_data["creator_username"]
        num_players = json_data["num_players"]
        setting = json_data["setting"]
        game_start_json = json_data["game_start"]
        game_start = None if game_start_json is None else GameStart.from_json(game_start_json)
        users = {k: UserInfo.from_json(v) for k, v in json_data["users"].items()}
        return cls(creator_username, num_players, setting, game_start, users)

    def save(self, code: int):
        folder_name = str(code)
        os.makedirs(folder_name, exist_ok=True)
        file_path = os.path.join(folder_name, "game_state.json")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)

    @classmethod
    def get(cls, code: int):
        folder_name = str(code)
        file_path = os.path.join(folder_name, "game_state.json")
        with open(file_path, 'r', encoding='utf-8') as f:
            return cls.from_json(json.load(f))

    @staticmethod
    def add_user(code: int, username: str, character=None):
        game_state = GameState.get(code)
        print("sas", UserInfo(username, character))
        game_state.users.update({username: UserInfo(username, character)})
        game_state.save(code)

    @staticmethod
    def add_num_players(code: int, num_players: int):
        game_state = GameState.get(code)
        game_state.num_players = num_players
        game_state.save(int(code))

    @staticmethod
    def add_setting(code: int, setting: str):
        game_state = GameState.get(code)
        game_state.setting = setting
        game_state.save(int(code))

    @staticmethod
    def add_game_start(code: int, game_start: GameStart):
        game_state = GameState.get(code)
        game_state.game_start = game_start
        game_state.save(int(code))

    @staticmethod
    def create(code: int, creator_username):
        GameState(creator_username, None, None, None, {creator_username: UserInfo(creator_username, None)}).save(code)


@dataclass
class UserData:
    step: str
    code: int


class UsersData:
    def __init__(self):
        self.data: dict[str, UserData] = {}
        self.file_path = "users_data.json"
        self.load()

    def load(self):
        if not os.path.exists(self.file_path):
            self.data = {}
            return

        with open(self.file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            self.data = {
                username: UserData(**user_data)
                for username, user_data in raw_data.items()
            }

    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(
                {username: asdict(user_data) for username, user_data in self.data.items()},
                f,
                ensure_ascii=False,
                indent=2
            )

    def update_step(self, username: str, step: str):
        if username not in self.data:
            self.data[username] = UserData(step=step, code=0)
        else:
            self.data[username].step = step
        self.save()

    def update_code(self, username: str, code: int):
        if username not in self.data:
            self.data[username] = UserData(step="", code=code)
        else:
            self.data[username].code = code
        self.save()

    def get_user_info(self, username: str):
        return self.data.get(username)
