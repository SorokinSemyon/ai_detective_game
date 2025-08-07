#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from game_handler import GameHandler


class ConsoleIO:
    def output(self, message: str):
        print(message)

    def input(self, prompt: str = "") -> str:
        return input(prompt)


if __name__ == "__main__":
    io = ConsoleIO()
    username = io.input("Введите username: ")
    handler = GameHandler(io, username)

    while True:
        user_info = handler.users_data.get_user_info(username)
        current_step = "unknown_user" if user_info is None else user_info.step

        if current_step in ["unknown_user"]:
            action = None
        else:
            action = io.input(f"({current_step}) > ")

        handler.process(action)
