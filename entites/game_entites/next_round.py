import json
from dataclasses import asdict
from pathlib import Path

from entites.cached_prompt_result import CachedPromptResult
from entites.game_entites.discovery import Discovery
from entites.game_entites.game_start import GameStart
from entites.game_entites.prompts.prompt import Prompt
from entites.prompt_executor import PromptExecutor


class NextRoundGenerator:
    def __init__(self, setting: str, num_players: int, game_start: GameStart, discoveries: list[Discovery],
                 use_cache: bool = True):
        self.setting = setting
        self.num_players = num_players
        self.use_cache = use_cache
        params = asdict(game_start)
        params.setdefault("discoveries", discoveries)
        params.setdefault("setting", setting)
        self.prompt = Prompt.from_file("next_round",
                                       {"{input_json}": json.dumps(params, indent=4, ensure_ascii=False)})

    def generate(self):
        prompt_executor = PromptExecutor(self.prompt)
        if self.use_cache:
            mock_path = Path(f"{self.setting}_{self.num_players}/next_round.txt")
            data = CachedPromptResult.from_file_text(mock_path, prompt_executor)
        else:
            data = prompt_executor.generate_text()

        return data
