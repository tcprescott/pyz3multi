import asyncio
from pyz3multi.bot import MultiworldBot
from pyz3multi.types import MessageType
from dotenv import load_dotenv
import os

load_dotenv()

multiworldbot = MultiworldBot(
    token=os.getenv("BOT_TOKEN"),
    name=os.getenv("BOT_NAME")
)

async def do_stuff():
    multiworld = await multiworldbot.join('aa753aad-5ca8-4270-be64-41dc3af3f16a')
    await multiworld.raw_send(
        payload = {
            'type': MessageType.Destroy,
            'sender': self.token,
            'save': False
        }
    )

    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(multiworldbot.start())
    loop.create_task(do_stuff())
    loop.run_forever()