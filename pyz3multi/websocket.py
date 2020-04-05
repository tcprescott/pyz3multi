__version__ = '0.0.1'

import asyncio
import json
import logging
import os
import uuid

import websockets

from pyz3multi.backoff import ExponentialBackoff
from pyz3multi.types import MessageType

log = logging.getLogger(__name__)

class pyz3multiException(Exception):
    pass

class BasicMultiworldClient():
    def __init__(self, token, bot):
        self.bot = bot
        self.socket = None

    async def connect(self):
        self.loop = asyncio.get_event_loop()

        log.debug(f"Connecting to Multiworld Service at {self.base_address}/{self.endpoint} ...")

        try:
            self.socket = await websockets.connect(f"{self.base_address}/{self.endpoint}", ping_timeout=None, ping_interval=None)
            self._listener = asyncio.create_task(self.listen())
        except Exception as e:
            if self.socket is not None:
                if not self.socket.closed:
                    await self.socket.close()
                self.socket = None

    async def raw_send(self, payload):
        if self.socket is None or not self.socket.open or self.socket.closed:
            return None

        try:
            await self.socket.send(json.dumps(payload))
        except Exception as e:
            if self.socket is not None:
                if not self.socket.closed:
                    await self.socket.close()
                self.socket = None
        
        log.debug(f'Payload sent to {self.endpoint} - {json.dumps(payload)}')

    async def on_raw_message(self, payload):
        log.debug(f'Payload received from {self.endpoint} - {json.dumps(payload)}')

    async def listen(self):
        while True:
            try:
                data = json.loads(await self.socket.recv())
                self.loop.create_task(self.on_raw_message(data))
            except websockets.ConnectionClosed:
                return self.loop.create_task(self.reconnection())

    async def reconnection(self):
        backoff = ExponentialBackoff()
        self._listener.cancel()

        while True:
            retry = backoff.delay()
            log.debug('PubSub Websocket closed: Retrying connection in %s seconds...', retry)

            await self.connect()

            await asyncio.sleep(retry)

    async def disconnect(self):
        if self.socket is None or not self.socket.open or self.socket.closed:
            return None
        
        await self.socket.close()
        self.reconnect = False

class Lobby(BasicMultiworldClient):
    def __init__(self, bot):
        self.bot = bot
        self.socket = None
        self.base_address = 'wss://mw.alttpr.com'
    
    @property
    def endpoint(self):
        return 'api/lobby/'

    async def lobby_request(self):
        await self.raw_send(
            payload = {
                'type': MessageType.LobbyRequest,
                'sender': self.bot.token,
            }
        )

    async def create(self, name, description, password="", finish_resolution=0, forfeit_resolution=0, item_animation=0, item_jingle=0, item_toast=0):
        await self.raw_send(
            payload = {
                'type': MessageType.Create,
                'sender': self.bot.token,
                'name': name,
                'description': description,
                'password': password,
                'finishResolution': finish_resolution,
                'forfeitResolution': forfeit_resolution,
                'itemAnimation': item_animation,
                'itemJingle': item_jingle,
                'itemToast': item_toast,
                'creationToken': str(uuid.uuid4())
            }
        )

class Game(BasicMultiworldClient):
    def __init__(self, guid, bot, name, description, has_password, game, world_count, gamemode):
        self.bot = bot
        self.socket = None
        self.base_address = 'wss://mw.alttpr.com'
        self.gamemode = gamemode
        self.name = name
        self.description = description
        self.has_password = has_password
        self.game = guid
        self.world_count = world_count

    @property
    def endpoint(self):
        return f'api/s1p/{self.guid}' if gamemode == 1 else f'api/mw/{self.guid}'

    async def knock(self, password=""):
        await self.raw_send(
            payload = {
                'type': MessageType.Knock,
                'sender': self.token,
                'playerName': self.name,
                'password': password if self.has_password else ""
            }
        )

    async def destroy(self):
        if socket is None:
            self.connect()

        await self.raw_send(
            payload = {
                'type': MessageType.Destroy,
                'sender': self.token,
                'save': False
            }
        )

    def __str__(self):
        return self.game

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'name={self.name!r}, game={self.game!r})')