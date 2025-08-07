import random
from dataclasses import dataclass

from entites.game_entites.game_start import GameStartGenerator
from entites.game_entites.game_state import GameState
from entites.game_entites.player_memories import KillerMemoriesGenerator, PlayerMemoriesGenerator


@dataclass
class Discovery:
    finder: str
    target: str
    evidence_found: str
    is_discovery_explicit: bool

    @classmethod
    def from_json(cls, json_data: dict):
        finder = json_data["finder"]
        target = json_data["target"]
        evidence_found = json_data["evidence_found"]
        is_discovery_explicit = json_data["is_discovery_explicit"]
        return cls(finder, target, evidence_found, is_discovery_explicit)

    @classmethod
    def calc_discoveries(cls, game_state: GameState):
        game_start = GameStartGenerator(game_state.setting, game_state.num_players).generate()
        result = []
        targets = []
        for user in game_state.users.values():
            is_secret_found = random.choice([True, False])
            if user.discovery_action == "Искать улики":
                is_killer_found = random.choice([True, False])
                if is_killer_found:
                    discovery_target = game_state.killer
                else:
                    discovery_target = random.choice(list(game_state.users.values())).character
            if user.discovery_action.startswith("Присматриваться к "):
                discovery_target = user.discovery_action.removeprefix("Присматриваться к ")
            if user.discovery_action.startswith("Подставить "):
                is_secret_found = True
                discovery_target = user.discovery_action.removeprefix("Подставить ")

            if discovery_target == game_state.killer:
                memories = KillerMemoriesGenerator(
                    game_state.setting, game_state.num_players, game_start, discovery_target
                ).generate()
            else:
                memories = PlayerMemoriesGenerator(
                    game_state.setting, game_state.num_players, game_start, discovery_target
                ).generate()

            if discovery_target not in targets:
                result.append(
                    Discovery(user.character, discovery_target, memories.hidden_evidence, is_secret_found)
                )
                targets.append(discovery_target)

        return result
