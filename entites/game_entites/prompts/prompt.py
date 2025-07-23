from dataclasses import dataclass
from pathlib import Path


@dataclass
class Prompt:
    system_prompt: str
    user_prompt: str

    def messages(self):
        return [
            {"role": "system", "text": self.system_prompt},
            {"role": "user", "text": self.user_prompt}
        ]

    @classmethod
    def from_file(cls, name: str, params: dict[str, str]):
        user_prompt_path = Path("entites/game_entites/prompts") / f"{name}_user_prompt.txt"
        system_prompt_path = Path("entites/game_entites/prompts") / f"{name}_system_prompt.txt"
        with open(user_prompt_path, 'r', encoding='utf-8') as file:
            user_prompt = file.read()
        with open(system_prompt_path, 'r', encoding='utf-8') as file:
            system_prompt = file.read()
        for k, v in params.items():
            user_prompt = user_prompt.replace(k, v)
        return cls(system_prompt, user_prompt)
