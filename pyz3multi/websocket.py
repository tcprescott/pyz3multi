__version__ = '0.0.1'

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime

import websockets

from pyz3multi.backoff import ExponentialBackoff
from pyz3multi.types import MessageType, ItemType, GameMode, ImportType

log = logging.getLogger(__name__)

ROOMREADY = {}

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

        # these will be sent in every payload
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
        
        if payload['type'] == MessageType.ImportRecords.value:
            log.info(f'Payload sent to {self.endpoint} - Import records request')
        else:
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
            if self.socket is None:
                return
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
        self._listener.cancel()
        await self.socket.close()
        self.socket = None

    async def chat(self, body: str):
        await self.raw_send(
            payload = {
                'type': MessageType.Chat.value,
                'body': body
            }
        )

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
        if payload['type'] == MessageType.LobbyEntry.value:
            if payload.get('destroyed', False):
                await self.cleanup_game(payload)
            else:
                await self.update_game(payload)
        if payload['type'] == MessageType.RoomReady.value:
            if payload['creationToken'] in ROOMREADY:
                await self.update_game(payload['game'])
                func = ROOMREADY[payload['creationToken']]
                if asyncio.iscoroutinefunction(func.func):
                    await func(game=self.bot.games[payload['game']['game']])
                else:
                    func(game=self.bot.games[payload['game']['game']])
                del ROOMREADY[payload['creationToken']]


    async def connect_handler(self):
        await self.lobby_request()

    async def lobby_request(self):
        await self.raw_send(
            payload = {
                'type': MessageType.LobbyRequest.value
            }
        )

    async def update_game(self, payload):
        if payload['game'] in self.bot.games:
            game = self.bot.get_game(payload['game'])
            game.name = payload.get('name', None)
            game.description = payload.get('description', None)
            game.has_password = payload.get('hasPassword', None)
            game.world_count = payload.get('worldCount', None)

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

    async def cleanup_game(self, payload):
        if payload['game'] in self.bot.games:
            game = self.bot.get_game(payload['game'])
            if game.socket is not None:
                await game.disconnect()
            try:
                del self.bot.games[payload['game']]
            except KeyError:
                log.info(f"Tried to remove {payload['game']} but was already removed!")

    async def create(
            self,
            name: str,
            description: str,
            password: str=None,
            mode=GameMode.Multiworld.value,
            finish_resolution: int=ItemType.Nothing.value,
            forfeit_resolution: int=ItemType.Nothing.value,
            item_animation: int=ItemType.Nothing.value,
            item_jingle: int=ItemType.Nothing.value,
            item_toast: int=ItemType.Nothing.value,
            creation_token: str=str(uuid.uuid4()),
            callback=None
        ):
        # task = asyncio.create_task()
        await self.raw_send(
            payload = {
                'type': MessageType.Create.value,
                'name': name,
                'description': description,
                'password': "" if password is None else password,
                'mode': mode,
                'finishResolution': finish_resolution,
                'forfeitResolution': forfeit_resolution,
                'itemAnimation': item_animation,
                'itemJingle': item_jingle,
                'itemToast': item_toast,
                'creationToken': creation_token
            }
        )
        if callback is not None:
            ROOMREADY[creation_token] = callback
        return creation_token

class Game(BasicMultiworldClient):
    def __init__(self, bot, name, description, has_password, game, world_count, created, mode, password=""):
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
        self.password = password
        self.players = {}
        self.worlds = {}

    @property
    def endpoint(self):
        return f'api/game/{self.game}'

    async def on_raw_message(self, payload):
        if payload['type'] == MessageType.ImportRecords.value:
            log.info(f'Payload received from {self.endpoint} - Import records request.')
        else:
            log.info(f'Payload received from {self.endpoint} - {json.dumps(payload)}')
        if payload['type'] == MessageType.Identify.value:
            player = Player(
                game = self,
                name = payload['name'],
                player_id = payload['sender']
            )
            self.players[payload['sender']] = player
        elif payload['type'] == MessageType.WorldDescription.value:
            world = World(
                game = self,
                world = payload['world'],
                title = payload['title'],
                description = payload['description'],
                rng = payload['rng'],
                mystery = payload.get('mystery', False),
                logic = payload.get('logic', {}),
                goals = payload.get('goals', {}),
                gameplay = payload.get('gameplay', {}),
                difficulty = payload.get('difficulty', {})
            )
            self.worlds[payload['world']] = world
        elif payload['type'] == MessageType.WorldClaim.value:
            self.worlds[payload['world']].claimed = payload['claim']
        elif payload['type'] == MessageType.ImportRecords.value:
            await self.knock()


    async def connect_handler(self):
        await self.knock()

    async def knock(self):
        if self.socket is None:
            self.connect()
        await self.raw_send(
            payload = {
                'type': MessageType.Knock.value,
                'playerName': self.bot.name,
                'password': self.password if self.has_password else ""
            }
        )

    async def import_records(self, body, import_type=ImportType.V31JSON.value):
        if self.socket is None:
            self.connect()
        await self.raw_send(
            payload = {
                'type': MessageType.ImportRecords.value,
                'body': body,
                'importType': import_type
            }
        )

    async def destroy(self, save=False):
        if self.socket is None:
            self.connect()
        await self.raw_send(
            payload = {
                'type': MessageType.Destroy.value,
                'save': save
            }
        )

    def get_player(self, guid):
        try:
            return self.players[guid]
        except KeyError:
            return None

    def get_world(self, world_id):
        try:
            return self.worlds[world_id]
        except KeyError:
            return None

    def __str__(self):
        return self.game

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'name={self.name!r}, game={self.game!r})')

class Player():
    def __init__(self, game, name, player_id):
        self.game = game
        self.name = name
        self.player_id = player_id

    async def kick(self, reason, resolution):
        if self.game.socket is None:
            self.game.connect()
        await self.game.raw_send(
            payload = {
                'type': MessageType.Kick.value,
                'target': self.player_id,
                'reason': reason,
                'resolution': resolution
            }
        )

class World():
    def __init__(self, game: Game, world: int, title: str, description: str, rng: str, mystery: bool, logic: dict, goals: dict, gameplay: dict, difficulty: dict):
        self.game = game
        self.world = world
        self.title = title
        self.description = description
        self.rng = rng
        self.mystery = mystery
        self.logic = logic
        self.goals = goals
        self.gameplay = gameplay
        self.difficulty = difficulty
        self.claimed = False
    
    async def claim(self):
        if self.game.socket is None:
            self.game.connect()
        await self.game.raw_send(
            payload = {
                'type': MessageType.WorldClaim.value,
                'world': self.world,
                'claim': True,
            }
        )

    async def unclaim(self):
        if self.game.socket is None:
            self.game.connect()
        await self.game.raw_send(
            payload = {
                'type': MessageType.WorldClaim.value,
                'world': self.world,
                'claim': False,
            }
        )