# -*- coding: utf-8 -*-

import json
from typing import List
from dataclasses import dataclass, asdict
from pathlib import Path

from entites.cached_prompt_result import CachedPromptResult
from entites.game_entites.prompts.prompt import Prompt
from entites.prompt_executor import PromptExecutor


@dataclass
class CrimeInfo:
    crime_scene: str
    victim: str
    initial_story: str
    isolation_reason: str

    @classmethod
    def from_json(cls, json_data: dict[str, str]):
        crime_scene = json_data["crime_scene"]
        victim = json_data["victim"]
        initial_story = json_data["initial_story"]
        isolation_reason = json_data["isolation_reason"]
        return cls(crime_scene, victim, initial_story, isolation_reason)


@dataclass
class Character:
    name: str
    role: str
    description: str

    @classmethod
    def from_json(cls, json_data: dict[str, str]):
        name = json_data["name"]
        role = json_data["role"]
        description = json_data["description"]
        return cls(name, role, description)


@dataclass
class GameStart:
    crime_info: CrimeInfo
    characters: List[Character]

    @classmethod
    def from_json(cls, json_data: dict):
        characters = [Character.from_json(char) for char in json_data["characters"]]
        return cls(CrimeInfo.from_json(json_data["crime_info"]), characters)


class GameStartGenerator:
    def __init__(self, setting: str, num_players: int, use_cache: bool = True):
        self.setting = setting
        self.num_players = num_players
        self.use_cache = use_cache
        self.prompt = Prompt.from_file("game_start", {"{setting}": setting, "{num_players}": str(num_players)})

    def generate(self):
        prompt_executor = PromptExecutor(self.prompt)
        if self.use_cache:
            mock_path = Path(f"{self.setting}_{self.num_players}/game_start.json")
            json_data = CachedPromptResult.from_file(mock_path, prompt_executor).value
        else:
            json_data = prompt_executor.generate()

        return GameStart.from_json(json_data)
