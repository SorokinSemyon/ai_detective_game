from pathlib import Path
import json

from entites.prompt_executor import PromptExecutor


class CachedPromptResult:
    def __init__(self, value: dict):
        self.value = value

    @classmethod
    def from_file(cls, path: Path, prompt_executor: PromptExecutor):
        full_path = Path("cached") / path
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as file:
                return cls(json.load(file))
        else:
            generated_data = prompt_executor.generate()
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file:
                json.dump(generated_data, file, ensure_ascii=False, indent=2)
            return cls(generated_data)

    @classmethod
    def from_file_text(cls, path: Path, prompt_executor: PromptExecutor):
        full_path = Path("cached") / path
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            generated_data = prompt_executor.generate_text()
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write(str(generated_data))
            return generated_data
