import json
from dataclasses import asdict

from entites.game_entites.discovery import Discovery
from entites.game_entites.game_start import GameStart
from entites.game_entites.prompts.prompt import Prompt


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
