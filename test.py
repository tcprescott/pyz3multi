import asyncio
from pyz3multi.bot import MultiworldBot
from pyz3multi.types import MessageType
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(filename='output/app.log', level=logging.DEBUG)
log = logging.getLogger(__name__)

multiworldbot = MultiworldBot(
    token=os.getenv("BOT_TOKEN"),
    name=os.getenv("BOT_NAME")
)

async def do_stuff():
    await multiworldbot.join('aa753aad-5ca8-4270-be64-41dc3af3f16a')

    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(multiworldbot.start())
    loop.create_task(do_stuff())
    loop.run_forever()