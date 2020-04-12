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
            self.update_game(payload)
        if payload['type'] == MessageType.RoomReady.value:
            if payload['creationToken'] in ROOMREADY:
                self.update_game(payload['game'])
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

    def update_game(self, payload):
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

    async def create(
            self,
            name: str,
            description: str,
            password: str="",
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
        if callback is not None:
            ROOMREADY[creation_token] = callback
        return creation_token

    # def register_room_create(self, creation_token, partial):
    #     ROOMREADY[creation_token] = partial


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

    async def knock(self, password=""):
        await self.raw_send(
            payload = {
                'type': MessageType.Knock.value,
                'playerName': self.bot.name,
                'password': password if self.has_password else ""
            }
        )

    async def import_records(self, body, import_type=ImportType.V31JSON.value):
        await self.raw_send(
            payload = {
                'type': MessageType.ImportRecords.value,
                'body': body,
                'importType': import_type
            }
        )

    async def destroy(self):
        await self.raw_send(
            payload = {
                'type': MessageType.Destroy.value,
                'save': False
            }
        )

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
        await self.game.raw_send(
            payload = {
                'type': MessageType.WorldClaim.value,
                'world': self.world,
                'claim': True,
            }
        )

    async def unclaim(self):
        await self.game.raw_send(
            payload = {
                'type': MessageType.WorldClaim.value,
                'world': self.world,
                'claim': False,
            }
        )