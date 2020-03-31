import asyncio
from pyz3multi.websocket import Lobby, Multiworld
from pyz3multi.types import MessageType

class MultiworldBot():
    def __init__(self, token, name):
        self.lobby = Lobby(bot=self)
        self.games = {}
        self.token = token
        self.name = name

    async def start(self):
        await self.lobby.connect()

    async def join(self, guid, gametype='mw', password=""):
        client = Multiworld(guid=guid, gametype='mw', bot=self)
        self.games[guid] = {
            'client': client,
            'gametype': gametype,
        }
        await client.connect()
        await client.raw_send(
            payload = {
                'type': MessageType.Knock,
                'sender': self.token,
                'playerName': self.name,
                'password': password
            }
        )
        return client