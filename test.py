import asyncio
from pyz3multi.bot import MultiworldBot
from pyz3multi.types import MessageType
from dotenv import load_dotenv
import os
import logging
import aioconsole
import shlex
import sys
import json

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

        if command[0] == 'request':
            await multiworldbot.lobby.lobby_request()
        
        if command[0] == 'connect':
            await multiworldbot.games[command[1]].connect()

        if command[0] == 'destroy':
            await multiworldbot.games[command[1]].destroy()

        if command[0] == 'create':
            creation_token = await multiworldbot.lobby.create(
                name=command[1],
                description="this is a test"
            )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(multiworldbot.start())
    loop.create_task(console())
    loop.run_forever()