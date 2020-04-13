import asyncio
import pyz3multi.websocket
from pyz3multi.types import MessageType

class MultiworldBot():
    def __init__(self, token, name):
        self.lobby = pyz3multi.websocket.Lobby(bot=self)
        self.games = {}
        self.token = token
        self.name = name

    def get_game(self, guid):
        try:
            return self.games[guid]
        except KeyError:
            return None

    async def start(self):
        await self.lobby.connect()