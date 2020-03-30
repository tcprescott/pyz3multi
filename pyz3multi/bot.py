import asyncio
from . import websocket

class MultiworldBot():
    def __init__(self):
        self.lobby = websocket.BasicMultiworldClient(endpoint='api/lobby/', bot=self)
        self.games = {}

    async def start(self):
        await self.lobby.connect()

    async def join(self, guid, gametype='mw'):
        endpoints = {
            'mw': f'api/mw/{guid}',
            's1p': f'api/s1p/{guid}'
        }
        self.games[guid] = {
            'client': websocket.BasicMultiworldClient(endpoint=endpoints[gametype], bot=self),
            'gametype': gametype,
        }
