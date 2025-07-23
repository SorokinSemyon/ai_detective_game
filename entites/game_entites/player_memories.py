import json
from dataclasses import dataclass, asdict
from pathlib import Path

from entites.cached_prompt_result import CachedPromptResult
from entites.game_entites.game_start import GameStart
from entites.game_entites.prompts.prompt import Prompt
from entites.prompt_executor import PromptExecutor


@dataclass
class PlayerMemories:
    secret: str
    motive: str
    hidden_evidence: str
    memories: str

    @classmethod
    def from_json(cls, json_data: dict):
        secret = json_data["secret"]
        motive = json_data["motive"]
        hidden_evidence = json_data["hidden_evidence"]
        memories = json_data["memories"]
        return cls(secret, motive, hidden_evidence, memories)


class KillerMemoriesGenerator:
    def __init__(self, setting: str, num_players: int, game_start: GameStart, killer_name: str, use_cache: bool = True):
        self.setting = setting
        self.num_players = num_players
        self.killer_name = killer_name
        self.use_cache = use_cache
        params = asdict(game_start)
        params.setdefault("killer", killer_name)
        params.setdefault("setting", setting)
        self.prompt = Prompt.from_file("killer_memories",
                                       {"{input_json}": json.dumps(params, indent=4, ensure_ascii=False)})

    def generate(self):
        prompt_executor = PromptExecutor(self.prompt)
        if self.use_cache:
            mock_path = Path(f"{self.setting}_{self.num_players}/{self.killer_name}/killer_memories.json")
            json_data = CachedPromptResult.from_file(mock_path, prompt_executor).value
        else:
            json_data = prompt_executor.generate()

        return PlayerMemories.from_json(json_data)


class PlayerMemoriesGenerator:
    def __init__(self, setting: str, num_players: int, game_start: GameStart, player_name: str, use_cache: bool = True):
        self.setting = setting
        self.num_players = num_players
        self.player_name = player_name
        self.use_cache = use_cache
        params = asdict(game_start)
        params.setdefault("player", player_name)
        params.setdefault("setting", setting)
        self.prompt = Prompt.from_file("player_memories",
                                       {"{input_json}": json.dumps(params, indent=4, ensure_ascii=False)})

    def generate(self):
        prompt_executor = PromptExecutor(self.prompt)
        if self.use_cache:
            mock_path = Path(f"{self.setting}_{self.num_players}/{self.player_name}/player_memories.json")
            json_data = CachedPromptResult.from_file(mock_path, prompt_executor).value
        else:
            json_data = prompt_executor.generate()

        return PlayerMemories.from_json(json_data)
