import asyncio
import pyz3multi.websocket
from pyz3multi.types import MessageType

class MultiworldBot():
    def __init__(self, token, name):
        self.lobby = pyz3multi.websocket.Lobby(bot=self)
        self.games = {}
        self.token = token
        self.name = name

    async def start(self):
        await self.lobby.connect()
        await self.lobby.lobby_request()

    async def join(self, guid, gametype='mw', password=""):
        client = pyz3multi.websocket.Game(guid=guid, gametype='mw', bot=self)
        self.games[guid] = {
            'client': client,
            'gametype': gametype,
        }
        await client.connect()

        return client