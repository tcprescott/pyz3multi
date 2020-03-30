import asyncio
from pyz3multi.bot import MultiworldBot

multiworldbot = MultiworldBot()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(multiworldbot.start())
    loop.run_forever()