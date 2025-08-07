import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from entites.game_entites.discovery import Discovery
from entites.game_entites.game_start import GameStartGenerator, GameStart
from entites.game_entites.next_round import NextRoundGenerator
from entites.game_entites.player_memories import PlayerMemoriesGenerator, KillerMemoriesGenerator

file_path = "tasks.json"


def load_tasks() -> list[dict[str, Any]]:
    if not Path(file_path).exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def add_game_start_task(setting: str, num_players: int):
    tasks = load_tasks()
    tasks.append({"generator": "GameStartGenerator", "args": {"setting": setting, "num_players": num_players}})
    save_tasks(tasks)


def add_player_memories_task(setting: str, num_players: int, game_start: GameStart, character: str):
    tasks = load_tasks()
    args = {
        "setting": setting,
        "num_players": num_players,
        "game_start": asdict(game_start),
        "character": character
    }
    tasks.append({"generator": "PlayerMemoriesGenerator", "args": args})
    save_tasks(tasks)


def add_killer_memories_task(setting: str, num_players: int, game_start: GameStart, character: str):
    tasks = load_tasks()
    args = {
        "setting": setting,
        "num_players": num_players,
        "game_start": asdict(game_start),
        "character": character
    }
    tasks.append({"generator": "KillerMemoriesGenerator", "args": args})
    save_tasks(tasks)

def add_next_round_task(setting: str, num_players: int, game_start: GameStart, discoveries: list[Discovery]):
    tasks = load_tasks()
    args = {
        "setting": setting,
        "num_players": num_players,
        "game_start": asdict(game_start),
        "discoveries": [asdict(d) for d in discoveries]
    }
    tasks.append({"generator": "NextRoundGenerator", "args": args})
    save_tasks(tasks)


def save_tasks(tasks) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)


def execute_generator(generator_name: str, args: dict[str, Any]):
    generator = None
    if generator_name == "GameStartGenerator":
        generator = GameStartGenerator(args["setting"], args["num_players"])
    elif generator_name == "PlayerMemoriesGenerator":
        generator = PlayerMemoriesGenerator(
            args["setting"], args["num_players"], GameStart.from_json(args["game_start"]), args["character"]
        )
    elif generator_name == "KillerMemoriesGenerator":
        generator = KillerMemoriesGenerator(
            args["setting"], args["num_players"], GameStart.from_json(args["game_start"]), args["character"]
        )
    elif generator_name == "NextRoundGenerator":
        generator = NextRoundGenerator(
            args["setting"], args["num_players"], GameStart.from_json(args["game_start"]), args["discoveries"]
        )
    return generator.generate()


def task_executor():
    while True:
        tasks = load_tasks()

        if not tasks:
            print("Нет задач. Жду 5 секунд...")
            time.sleep(5)
            continue

        task = tasks[0]
        print(f"Выполняю: {task['generator']}({task['args']})")

        try:
            execute_generator(task["generator"], task["args"])
            tasks.pop(0)
            save_tasks(tasks)
            print("✅ Успешно!")
        except Exception as e:
            print(f"Ошибка: {e}. Задача остаётся в очереди.")
            time.sleep(5)


if __name__ == "__main__":
    task_executor()
