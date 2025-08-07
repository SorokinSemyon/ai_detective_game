#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from dataclasses import dataclass, asdict


@dataclass
class UserInfo:
    username: str
    character: str
    discovery_action: str

    @classmethod
    def from_json(cls, json_data):
        username = json_data["username"]
        character = json_data["character"]
        discovery_action = json_data["discovery_action"]
        return cls(username, character, discovery_action)


@dataclass
class GameState:
    creator_username: str
    num_players: int
    setting: str
    killer: str
    users: dict[str, UserInfo]

    @classmethod
    def from_json(cls, json_data):
        creator_username = json_data["creator_username"]
        num_players = json_data["num_players"]
        setting = json_data["setting"]
        killer = json_data["killer"]
        users = {k: UserInfo.from_json(v) for k, v in json_data["users"].items()}
        return cls(creator_username, num_players, setting, killer, users)


class GameStateRoom:
    def __init__(self, code):
        self.code = code
        folder_name = f"rooms/{code}"
        os.makedirs(folder_name, exist_ok=True)
        self.file_path = os.path.join(folder_name, "game_state.json")

    def save(self, game_state: GameState):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(game_state), f, ensure_ascii=False, indent=2)

    def get_state(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return GameState.from_json(json.load(f))

    def add_user(self, username: str, character=None):
        game_state = self.get_state()
        game_state.users.update({username: UserInfo(username, character, None)})
        self.save(game_state)

    def add_user_discovery_action(self, username: str, discovery_action: str):
        game_state = self.get_state()
        user = game_state.users[username]
        user.discovery_action = discovery_action
        game_state.users.update({username: user})
        self.save(game_state)

    def add_num_players(self, num_players: int):
        game_state = self.get_state()
        game_state.num_players = num_players
        self.save(game_state)

    def add_setting(self, setting: str):
        game_state = self.get_state()
        game_state.setting = setting
        self.save(game_state)

    def add_killer(self, killer: str):
        game_state = self.get_state()
        game_state.killer = killer
        self.save(game_state)

    def create(self, creator_username):
        game_state = GameState(creator_username, None, None, None,
                               {creator_username: UserInfo(creator_username, None, None)})
        self.save(game_state)


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

    def delete(self, username: str):
        del self.data[username]
        self.save()
