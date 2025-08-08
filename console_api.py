#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from game_handler import GameHandler


class ConsoleIO:
    async def output(self, message: str):
        print(message)

    async def input(self, prompt: str = "") -> str:
        return input(prompt)


async def main():
    io = ConsoleIO()
    username = input("Введите username: ")
    handler = GameHandler(io, username)

    while True:
        user_input = await io.input("> ")
        await handler.process(user_input)


if __name__ == "__main__":
    asyncio.run(main())