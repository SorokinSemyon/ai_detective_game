import random
import textwrap
from dataclasses import asdict

from entites.game_entites.discovery import Discovery
from entites.game_entites.game_start import GameStartGenerator
from entites.game_entites.game_state import UsersData, GameStateRoom
from entites.game_entites.next_round import NextRoundGenerator
from entites.game_entites.player_memories import PlayerMemoriesGenerator, KillerMemoriesGenerator
from entites.master_messages.master_messages import master_message
import task_executor


class GameHandler:
    def __init__(self, io_adapter, username: str):
        self.io = io_adapter
        self.username = username
        self.handlers = {
            "unknown_user": self.handle_unknown_user,
            "start": self.handle_start,
            "exit": self.handle_exit,
            "input_num_players": self.handle_input_num_players,
            "input_setting": self.handle_input_setting,
            "waiting_players": self.handle_waiting_players,
            "character_choice": self.handle_character_choice,
            "waiting_start": self.handle_waiting_start,
            "player_memories": self.handle_player_memories,
            "discovery_action": self.handle_discovery_action,
            "waiting_next_round": self.handle_waiting_next_round
        }
        self.users_data = UsersData()

    def process(self, action: str = None):
        user_info = self.users_data.get_user_info(self.username)
        step = "unknown_user" if user_info is None else user_info.step

        if action == "Выйти":
            step = "exit"
        if step in self.handlers:
            self.handlers[step](action)
        else:
            self.io.output(f"Unknown step: {step}")

    def change_user_step(self, next_step):
        self.users_data.update_step(self.username, next_step)

    def add_user_to_room(self, code):
        self.users_data.update_code(self.username, code)

    def get_user_room(self):
        code = self.users_data.get_user_info(self.username).code
        return GameStateRoom(code)

    def handle_unknown_user(self, action: str):
        self.io.output(master_message("app_start"))
        self.io.output("Действия: [Создать игру] или введите код игры")
        self.change_user_step("start")

    def handle_start(self, action: str):
        if action == "Создать игру":
            # code = random.randint(10000, 99999)
            code = 20000
            room = GameStateRoom(code)
            room.create(self.username)
            self.add_user_to_room(code)
            self.io.output(master_message("input_num_players"))
            self.change_user_step("input_num_players")
        elif action and action.isdigit():
            code = int(action)
            room = GameStateRoom(code)
            room.add_user(self.username)
            self.add_user_to_room(code)
            self.io.output("Вы присоединились к игре")
            self.handle_waiting_players()
            self.change_user_step("waiting_players")

    def handle_exit(self, action: str):
        self.users_data.delete(self.username)

    def handle_input_num_players(self, action: str):
        try:
            num_players = int(action)
            if 1 <= num_players <= 8:
                room = self.get_user_room()
                room.add_num_players(num_players)
                self.change_user_step("input_setting")
                self.io.output(master_message("input_setting"))
            else:
                self.io.output(master_message("wrong_num_players"))
        except ValueError:
            self.io.output(master_message("wrong_num_players"))

    def handle_input_setting(self, action: str):
        if len(action) < 42:
            room = self.get_user_room()
            room.add_setting(action)
            num_players = room.get_state().num_players
            task_executor.add_game_start_task(action, num_players)
            self.io.output(f"Сообщите своим друзьям код, чтобы они могли присоединиться к игре: {room.code}")
            self.handle_waiting_players()
            self.change_user_step("waiting_players")
        else:
            self.io.output(master_message("wrong_setting"))

    def handle_waiting_players(self, action: str = None):
        room = self.get_user_room()
        game_state = room.get_state()
        game_start_generator = GameStartGenerator(game_state.setting, game_state.num_players)

        if game_state and game_start_generator.exists():
            game_start = game_start_generator.generate()

            killer = random.choice(game_start.characters)
            room.add_killer(killer.name)

            for char in game_start.characters:
                if char == killer:
                    task_executor.add_killer_memories_task(
                        game_state.setting, game_state.num_players, game_start, char.name
                    )
                else:
                    task_executor.add_player_memories_task(
                        game_state.setting, game_state.num_players, game_start, char.name
                    )

            self.io.output(f"Сценарий: {game_state.setting}")
            self.io.output(master_message("game_start", params=asdict(game_start.crime_info)))

            self.io.output("\nПерсонажи:")
            for character in game_start.characters:
                current_player = "Свободен"
                for user_id, user_info in game_state.users.items():
                    if user_info.character == character.name:
                        current_player = user_id
                char_info = (
                    f"Имя: {character.name} ({current_player})\n"
                    f"Роль: {character.role}\n"
                    f"Описание: {textwrap.fill(character.description, width=100)}\n"
                )
                self.io.output(char_info)
            self.io.output("Введите имя персонажа:")
            self.change_user_step("character_choice")
        else:
            status = f"Ожидаем игроков ({len(game_state.users)}/{game_state.num_players})"
            self.io.output(status)
            self.io.output("Действия: [Обновить]")

    def handle_character_choice(self, action: str):
        room = self.get_user_room()
        user_character = action

        if user_character:
            room.add_user(self.username, action)
            self.io.output(f"Вы выбрали: {user_character}")
            self.handle_waiting_start()
            self.change_user_step("waiting_start")

    def handle_waiting_start(self, action: str = None):
        room = self.get_user_room()
        game_state = room.get_state()
        ready_players = sum(1 for u in game_state.users.values() if u.character)

        if ready_players == game_state.num_players:
            self.change_user_step("player_memories")
        else:
            status = f"Ожидаем выбор персонажей ({ready_players}/{game_state.num_players})"
            self.io.output(status)

    def handle_player_memories(self, action: str):
        room = self.get_user_room()
        game_state = room.get_state()
        character = game_state.users[self.username].character
        game_start = GameStartGenerator(game_state.setting, game_state.num_players).generate()

        if game_state.killer == character:
            memories = KillerMemoriesGenerator(
                game_state.setting,
                game_state.num_players,
                game_start,
                character
            ).generate()
            message_type = "killer_memories"
        else:
            memories = PlayerMemoriesGenerator(
                game_state.setting, game_state.num_players, game_start, character
            ).generate()
            message_type = "player_memories"

        self.io.output(master_message(message_type, params=asdict(memories)))
        self.change_user_step("discovery_action")

    def handle_discovery_action(self, action: str):
        if action is None:
            self.io.output("Опишите ваше действие:")
            return

        room = self.get_user_room()
        room.add_user_discovery_action(self.username, action)
        count_users_discovery_action = 0
        game_state = room.get_state()
        for user in game_state.users.values():
            if user.discovery_action is not None:
                count_users_discovery_action += 1

        if count_users_discovery_action == game_state.num_players:
            discoveries = Discovery.calc_discoveries(game_state)
            game_start = GameStartGenerator(game_state.setting, game_state.num_players).generate()
            task_executor.add_next_round_task(game_state.setting, game_state.num_players, game_start, discoveries)

        self.change_user_step("waiting_next_round")
        self.io.output("Действие сохранено")

    def handle_waiting_next_round(self, action: str):
        if action == "Готово":
            room = self.get_user_room()
            game_state = room.get_state()
            game_start = GameStartGenerator(game_state.setting, game_state.num_players).generate()
            discoveries = Discovery.calc_discoveries(game_state)
            next_round = NextRoundGenerator(
                game_state.setting, game_state.num_players, game_start, [asdict(d) for d in discoveries]
            ).generate()
            self.io.output(next_round)
            self.io.output(
                "Обсудите в последний раз новую информацию и затем проголосуйте за персонажа, которого больше всего подозреваете. "
                "Тот кто наберет больше всех голосов, должен раскрыть свой секрет."
            )
        else:
            self.io.output("Рекомендуемое время обсуждения: 10 мин")
            self.io.output("Действия: [Готово]")
