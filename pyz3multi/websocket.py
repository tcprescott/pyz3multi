__version__ = '0.0.1'

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime

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
            await self.connect_handler()
        except Exception as e:
            if self.socket is not None:
                if not self.socket.closed:
                    await self.socket.close()
                self.socket = None

    async def raw_send(self, payload):
        if self.socket is None or not self.socket.open or self.socket.closed:
            await self.connect()

        payload['id'] = str(uuid.uuid4())
        payload['created'] = int(datetime.utcnow().timestamp())
        payload['sender'] = self.bot.token

        try:
            await self.socket.send(json.dumps(payload))
        except Exception as e:
            if self.socket is not None:
                if not self.socket.closed:
                    await self.socket.close()
                self.socket = None
        
        log.info(f'Payload sent to {self.endpoint} - {json.dumps(payload)}')

    async def on_raw_message(self, payload):
        log.info(f'Payload received from {self.endpoint} - {json.dumps(payload)}')

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
            log.info('PubSub Websocket closed: Retrying connection in %s seconds...', retry)

            await self.connect()

            if self.socket is not None and self.socket.open:
                log.info(f'Reconnected to {self.endpoint}')
                return

            await asyncio.sleep(retry)

    async def connect_handler(self):
        pass

    async def disconnect(self):
        if self.socket is None or not self.socket.open or self.socket.closed:
            return None
        
        await self.socket.close()

class Lobby(BasicMultiworldClient):
    def __init__(self, bot):
        self.bot = bot
        self.socket = None
        self.base_address = 'wss://mw.alttpr.com'
    
    @property
    def endpoint(self):
        return 'api/lobby/'

    async def on_raw_message(self, payload):
        log.info(f'Payload received from {self.endpoint} - {json.dumps(payload)}')
        if payload['type'] == MessageType.LobbyEntry:
            if payload['game'] in self.bot.games:
                self.bot.games[payload['game']].name = payload.get('name', None)
                self.bot.games[payload['game']].description = payload.get('description', None)
                self.bot.games[payload['game']].has_password = payload.get('hasPassword', None),
                self.bot.games[payload['game']].world_count = payload.get('worldCount', None),
            else:
                self.bot.games[payload['game']] = Game(
                    bot=self.bot,
                    name=payload.get('name', None),
                    description=payload.get('description', None),
                    has_password=payload.get('hasPassword', None),
                    game=payload.get('game', None),
                    world_count=payload.get('worldCount', None),
                    created=datetime.utcfromtimestamp(payload.get('created', None)),
                    mode=payload.get('mode', None),
                )

    async def connect_handler(self):
        await self.lobby_request()

    async def lobby_request(self):
        await self.raw_send(
            payload = {
                'type': MessageType.LobbyRequest
            }
        )

    async def create(
            self,
            name,
            description,
            password="",
            mode=2,
            finish_resolution=0,
            forfeit_resolution=0,
            item_animation=0,
            item_jingle=0,
            item_toast=0,
            creation_token: str=str(uuid.uuid4())
        ):
        await self.raw_send(
            payload = {
                'type': MessageType.Create,
                'name': name,
                'description': description,
                'password': password,
                'mode': mode,
                'finishResolution': finish_resolution,
                'forfeitResolution': forfeit_resolution,
                'itemAnimation': item_animation,
                'itemJingle': item_jingle,
                'itemToast': item_toast,
                'creationToken': creation_token
            }
        )
        return creation_token

class Game(BasicMultiworldClient):
    def __init__(self, bot, name, description, has_password, game, world_count, created, mode):
        self.bot = bot
        self.socket = None
        self.base_address = 'wss://mw.alttpr.com'
        self.name = name
        self.description = description
        self.has_password = has_password
        self.game = game
        self.world_count = world_count
        self.created = created
        self.mode = mode
        self.players = {}
        self.worlds = []

    @property
    def endpoint(self):
        return f'api/game/{self.game}'

    async def on_raw_message(self, payload):
        log.info(f'Payload received from {self.endpoint} - {json.dumps(payload)}')
        if payload['type'] == MessageType.Identify:
            if payload['sender'] in self.players:
                self.players[payload['sender']]['name'] = payload.get('name', None)
            else:
                self.players[payload['sender']] = {
                    'name': payload.get('name', None),
                    'id': payload.get('sender', None),
                }

    async def connect_handler(self):
        await self.knock()

    async def knock(self, password=""):
        await self.raw_send(
            payload = {
                'type': MessageType.Knock,
                'playerName': self.bot.name,
                'password': password if self.has_password else ""
            }
        )

    async def destroy(self):
        await self.raw_send(
            payload = {
                'type': MessageType.Destroy,
                'save': False
            }
        )

    def __str__(self):
        return self.game

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'name={self.name!r}, game={self.game!r})')