import asyncio
import functools
import gzip
import json
import logging
import os
import shlex
import sys

import aioconsole
import aiohttp
from dotenv import load_dotenv

from pyz3multi.bot import MultiworldBot
from pyz3multi.types import GameMode, ImportType, ItemType, MessageType

load_dotenv()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

multiworldbot = MultiworldBot(
    token=os.getenv("BOT_TOKEN"),
    name=os.getenv("BOT_NAME")
)

async def console():
    while True:
        msg = await aioconsole.ainput()

        command = shlex.split(msg)
        if not command:
            continue

        if command[0] == 'import':
            game = multiworldbot.games[command[1]]
            settings = {
                "worlds":{
                    "1":{
                        "preset":"default",
                        "glitches_required":"none",
                        "item_placement":"advanced",
                        "dungeon_items":"standard",
                        "accessibility":"items",
                        "goal":"ganon",
                        "tower_open":"7",
                        "ganon_open":"7",
                        "world_state":"open",
                        "entrance_shuffle":"none",
                        "boss_shuffle":"none",
                        "enemy_shuffle":"none",
                        "hints":"on",
                        "weapons":"randomized",
                        "item_pool":"normal",
                        "item_functionality":"normal",
                        "enemy_damage":"default",
                        "enemy_health":"default",
                        "spoiler":"off"
                    },
                    "2":{
                        "preset":"default",
                        "glitches_required":"none",
                        "item_placement":"advanced",
                        "dungeon_items":"standard",
                        "accessibility":"items",
                        "goal":"ganon",
                        "tower_open":"7",
                        "ganon_open":"7",
                        "world_state":"open",
                        "entrance_shuffle":"none",
                        "boss_shuffle":"none",
                        "enemy_shuffle":"none",
                        "hints":"on",
                        "weapons":"randomized",
                        "item_pool":"normal",
                        "item_functionality":"normal",
                        "enemy_damage":"default",
                        "enemy_health":"default",
                        "spoiler":"off"
                    },
                    "3":{
                        "preset":"default",
                        "glitches_required":"none",
                        "item_placement":"advanced",
                        "dungeon_items":"standard",
                        "accessibility":"items",
                        "goal":"ganon",
                        "tower_open":"7",
                        "ganon_open":"7",
                        "world_state":"open",
                        "entrance_shuffle":"none",
                        "boss_shuffle":"none",
                        "enemy_shuffle":"none",
                        "hints":"on",
                        "weapons":"randomized",
                        "item_pool":"normal",
                        "item_functionality":"normal",
                        "enemy_damage":"default",
                        "enemy_health":"default",
                        "spoiler":"off"
                    },
                    "4":{
                        "preset":"default",
                        "glitches_required":"none",
                        "item_placement":"advanced",
                        "dungeon_items":"standard",
                        "accessibility":"items",
                        "goal":"ganon",
                        "tower_open":"7",
                        "ganon_open":"7",
                        "world_state":"open",
                        "entrance_shuffle":"none",
                        "boss_shuffle":"none",
                        "enemy_shuffle":"none",
                        "hints":"on",
                        "weapons":"randomized",
                        "item_pool":"normal",
                        "item_functionality":"normal",
                        "enemy_damage":"default",
                        "enemy_health":"default",
                        "spoiler":"off"
                    },
                    "5":{
                        "preset":"default",
                        "glitches_required":"none",
                        "item_placement":"advanced",
                        "dungeon_items":"standard",
                        "accessibility":"items",
                        "goal":"ganon",
                        "tower_open":"7",
                        "ganon_open":"7",
                        "world_state":"open",
                        "entrance_shuffle":"none",
                        "boss_shuffle":"none",
                        "enemy_shuffle":"none",
                        "hints":"on",
                        "weapons":"randomized",
                        "item_pool":"normal",
                        "item_functionality":"normal",
                        "enemy_damage":"default",
                        "enemy_health":"default",
                        "spoiler":"off"
                    },
                    "6":{
                        "preset":"default",
                        "glitches_required":"none",
                        "item_placement":"advanced",
                        "dungeon_items":"standard",
                        "accessibility":"items",
                        "goal":"ganon",
                        "tower_open":"7",
                        "ganon_open":"7",
                        "world_state":"open",
                        "entrance_shuffle":"none",
                        "boss_shuffle":"none",
                        "enemy_shuffle":"none",
                        "hints":"on",
                        "weapons":"randomized",
                        "item_pool":"normal",
                        "item_functionality":"normal",
                        "enemy_damage":"default",
                        "enemy_health":"default",
                        "spoiler":"off"
                    }
                },
                "lang":"en"
            }
            async with aiohttp.request(
                method='post',
                url='https://v311test.synack.live/api/multiworld',
                json=settings,
                auth=aiohttp.BasicAuth('mirrorshield', 'isariot')
            ) as resp:
                print(resp)
                binary = await resp.read()
            records = gzip.decompress(binary).decode('utf-8')
            await game.import_records(records)

        if command[0] == 'request':
            await multiworldbot.lobby.lobby_request()
        
        if command[0] == 'connect':
            game = multiworldbot.games[command[1]]
            await game.connect()

        if command[0] == 'destroy':
            game = multiworldbot.games[command[1]]
            await game.destroy()

        if command[0] == 'claim':
            game = multiworldbot.games[command[1]]
            await game.worlds[int(command[2])].claim()

        if command[0] == 'unclaim':
            game = multiworldbot.games[command[1]]
            await game.worlds[int(command[2])].unclaim()

        if command[0] == 'create':
            creation_token = await multiworldbot.lobby.create(
                name=command[1],
                description="this is a test",
                mode=GameMode.Multiworld.value,
                callback=functools.partial(fire_after_room_creation)
            )

        if command[0] == 'chat':
            if command[1] == 'lobby':
                await multiworldbot.lobby.chat(command[2])
            else:
                game = multiworldbot.games[command[1]]
                await game.chat(command[2])

async def fire_after_room_creation(game):
    await game.connect()
    settings = {
        "worlds":{
            "1":{
                "preset":"default",
                "glitches_required":"none",
                "item_placement":"advanced",
                "dungeon_items":"standard",
                "accessibility":"items",
                "goal":"ganon",
                "tower_open":"7",
                "ganon_open":"7",
                "world_state":"open",
                "entrance_shuffle":"none",
                "boss_shuffle":"none",
                "enemy_shuffle":"none",
                "hints":"on",
                "weapons":"randomized",
                "item_pool":"normal",
                "item_functionality":"normal",
                "enemy_damage":"default",
                "enemy_health":"default",
                "spoiler":"off"
            },
            "2":{
                "preset":"default",
                "glitches_required":"none",
                "item_placement":"advanced",
                "dungeon_items":"standard",
                "accessibility":"items",
                "goal":"ganon",
                "tower_open":"7",
                "ganon_open":"7",
                "world_state":"open",
                "entrance_shuffle":"none",
                "boss_shuffle":"none",
                "enemy_shuffle":"none",
                "hints":"on",
                "weapons":"randomized",
                "item_pool":"normal",
                "item_functionality":"normal",
                "enemy_damage":"default",
                "enemy_health":"default",
                "spoiler":"off"
            },
            "3":{
                "preset":"default",
                "glitches_required":"none",
                "item_placement":"advanced",
                "dungeon_items":"standard",
                "accessibility":"items",
                "goal":"ganon",
                "tower_open":"7",
                "ganon_open":"7",
                "world_state":"open",
                "entrance_shuffle":"none",
                "boss_shuffle":"none",
                "enemy_shuffle":"none",
                "hints":"on",
                "weapons":"randomized",
                "item_pool":"normal",
                "item_functionality":"normal",
                "enemy_damage":"default",
                "enemy_health":"default",
                "spoiler":"off"
            },
            "4":{
                "preset":"default",
                "glitches_required":"none",
                "item_placement":"advanced",
                "dungeon_items":"standard",
                "accessibility":"items",
                "goal":"ganon",
                "tower_open":"7",
                "ganon_open":"7",
                "world_state":"open",
                "entrance_shuffle":"none",
                "boss_shuffle":"none",
                "enemy_shuffle":"none",
                "hints":"on",
                "weapons":"randomized",
                "item_pool":"normal",
                "item_functionality":"normal",
                "enemy_damage":"default",
                "enemy_health":"default",
                "spoiler":"off"
            },
            "5":{
                "preset":"default",
                "glitches_required":"none",
                "item_placement":"advanced",
                "dungeon_items":"standard",
                "accessibility":"items",
                "goal":"ganon",
                "tower_open":"7",
                "ganon_open":"7",
                "world_state":"open",
                "entrance_shuffle":"none",
                "boss_shuffle":"none",
                "enemy_shuffle":"none",
                "hints":"on",
                "weapons":"randomized",
                "item_pool":"normal",
                "item_functionality":"normal",
                "enemy_damage":"default",
                "enemy_health":"default",
                "spoiler":"off"
            },
            "6":{
                "preset":"default",
                "glitches_required":"none",
                "item_placement":"advanced",
                "dungeon_items":"standard",
                "accessibility":"items",
                "goal":"ganon",
                "tower_open":"7",
                "ganon_open":"7",
                "world_state":"open",
                "entrance_shuffle":"none",
                "boss_shuffle":"none",
                "enemy_shuffle":"none",
                "hints":"on",
                "weapons":"randomized",
                "item_pool":"normal",
                "item_functionality":"normal",
                "enemy_damage":"default",
                "enemy_health":"default",
                "spoiler":"off"
            }
        },
        "lang":"en"
    }
    async with aiohttp.request(
        method='post',
        url='https://v311test.synack.live/api/multiworld',
        json=settings,
        auth=aiohttp.BasicAuth(os.getenv("SITE_USERNAME"), os.getenv("SITE_PASSWORD"))
    ) as resp:
        print(resp)
        binary = await resp.read()
    records = gzip.decompress(binary).decode('utf-8')
    await game.import_records(records)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(multiworldbot.start())
    loop.create_task(console())
    loop.run_forever()
