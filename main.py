#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import textwrap
from dataclasses import asdict
import random
from entites.game_entites.discovery import Discovery
from entites.game_entites.game_start import GameStartGenerator, CrimeInfo
from entites.game_entites.game_state import GameState, UserInfo, UsersData
from entites.game_entites.next_round import NextRoundGenerator
from entites.game_entites.player_memories import KillerMemoriesGenerator, PlayerMemoriesGenerator, PlayerMemories
from entites.master_messages.master_messages import master_message


def handle_unknown_user(username: str, action: str):
    usersData = UsersData()
    if action == "Создать игру":
        # code = random.randint(10000, 99999)
        code = 39645
        GameState.create(code, username)
        usersData.update_step(username, "input_num_players")
        usersData.update_code(username, code)
        print("Сообщите своим друзьям код, чтобы они могли присоединиться к игре:", code)
    elif action.isdigit():
        print("Вы присоеднились")
        GameState.add_user(int(action), username)
        usersData.update_step(username, "waiting_players")
        usersData.update_code(username, int(action))


def handle_input_num_players(username: str, action: str):
    usersData = UsersData()
    try:
        num_players = int(action)
        print(num_players)
        if 3 <= num_players <= 8:
            usersData.update_step(username, "input_setting")
            GameState.add_num_players(usersData.get_user_info(username).code, num_players)
            return
    except ValueError:
        pass
    print(master_message("wrong_num_players"))


async def handle_input_setting(username: str, action: str):
    usersData = UsersData()
    setting = action
    if len(setting) < 42:
        usersData.update_step(username, "waiting_players")
        code = usersData.get_user_info(username).code
        GameState.add_setting(code, setting)
        num_players = GameState.get(code).num_players

        asyncio.create_task(
            generate_and_save_game_start(code, setting, num_players)
        )
        return

    print(master_message("wrong_setting"))


async def generate_and_save_game_start(code: str, setting: str, num_players: int):
    game_start = await asyncio.to_thread(GameStartGenerator(setting, num_players).generate())
    GameState.add_game_start(code, game_start)


def handle_waiting_players(username: str):
    users_data = UsersData()
    code = users_data.get_user_info(username).code
    game_state = GameState.get(code)
    if game_state.game_start is not None:
        usersData.update_step(username, "character_choice")
    else:
        print(f"Пока что ждем когда присоединяться другие игроки ({len(game_state.users)}/{game_state.num_players})")
        print("Кнопки действий: [Обновить]")


def handle_character_choice(username: str):
    users_data = UsersData()
    code = users_data.get_user_info(username).code
    game_state = GameState.get(code)
    game_start = game_state.game_start

    print(
        f"Пока ждете когда присоединяться другие игроки ({len(game_state.users)}/{game_state.num_players}) можете ознакомиться со сценарием и выбрать персонажа")
    print(master_message("game_start", params=asdict(game_start.crime_info)))
    print("\nПерсонажи:\n")
    character_names = []
    for character in game_start.characters:
        character_names.append(character.name)
        print("Имя: ", character.name)
        print("Роль: ", character.role)
        print("Описание: ", textwrap.fill(str(character.description), width=100))
        print()
    print("Введи имя персонажа, за которого хочешь играть")
    my_character = input()
    GameState.add_user(code, username, my_character)
    usersData.update_step(username, "waiting_start")


if __name__ == "__main__":
    input("Введите свой username: ")
    username = input()

    while True:
        usersData = UsersData()
        user_info = usersData.get_user_info(username)
        if user_info is None:
            print(master_message("app_start"))
            print("Кнопки действий: [Создать игру]")
            action = input()
            handle_unknown_user(username, action)
            continue
        step = user_info.step
        if step == "input_num_players":
            print(master_message("input_num_players"))
            action = input()
            handle_input_num_players(username, action)
        if step == "input_setting":
            print(master_message("input_setting"))
            action = input()
            asyncio.run(handle_input_setting(username, action))
        if step == "waiting_players":
            handle_waiting_players(username)
            action = input()
        if step == "character_choice":
            handle_character_choice(username)

    setting = "Древний Рим"
    num_players = 5
    game_start = GameStartGenerator(setting, num_players).generate()
    print("\nГерои:\n")
    character_names = []
    for character in game_start.characters:
        character_names.append(character.name)

    my_character = "Децим Юний Брут"
    killer_name = "Марк Туллий Веррес"
    player_names = character_names
    player_names.remove(killer_name)
    players_memories = {}
    for character in game_start.characters:
        memories = PlayerMemoriesGenerator(setting, num_players, game_start, character.name).generate()
        players_memories[character.name] = memories
        print(character.name, memories.hidden_evidence)

    discoveries = [Discovery("Децим Юний Брут", "Ливия Корнелия",
                             "Среди моих вещей найдены черновики завещания с явными признаками подчисток.", True),
                   Discovery("Ливия Корнелия", "Юлия Приска",
                             "В моём мешочке с травами найдены следы аконита, хотя я никогда не использовала его для лечения.",
                             True),
                   Discovery("Луций Клавдий Феликс", "Марк Туллий Веррес",
                             "Я не учел, что на одном из моих колец остался след от яда, когда открывал амфору.", False)
                   ]

    next_round = NextRoundGenerator(setting, num_players, game_start, [asdict(d) for d in discoveries])
    print(next_round.prompt.user_prompt)
    action = "Искать улики"
    if action == "Искать улики":
        is_killer_finded = random.choice([True, False])
        discovery_target = killer_name if is_killer_finded else random.choice(player_names)
        is_discovery_explicit = random.choice([True, False])
    else:  # action == "Наблюдать за {Имя персонажа}"
        discovery_target = action.removeprefix("Наблюдать за ")
        is_discovery_explicit = random.choice([True, False])
    Discovery(my_character, discovery_target, players_memories[discovery_target].hidden_evidence, is_discovery_explicit)
