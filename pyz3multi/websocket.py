__version__ = '0.0.1'

import websockets
import json

import asyncio
import os

import logging

from pyz3multi.types import MessageType
from pyz3multi.backoff import ExponentialBackoff

log = logging.getLogger(__name__)

class pyz3multiException(Exception):
    pass

class BasicMultiworldClient():
    def __init__(self, token, bot):
        self.bot = bot
        self.socket = None

    async def connect(self):
        self.loop = asyncio.get_event_loop()

        print(f"Connecting to Multiworld Service at {self.base_address}/{self.endpoint} ...")

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
        
        print(f'Payload sent to {self.endpoint} - {json.dumps(payload)}')

    async def process_receive(self, payload):
        print(f'Payload received from {self.endpoint} - {json.dumps(payload)}')

    async def listen(self):
        while True:
            try:
                data = json.loads(await self.socket.recv())
                self.loop.create_task(self.process_receive(data))
            except websockets.ConnectionClosed:
                return self.loop.create_task(self.reconnection())

    async def reconnection(self):
        backoff = ExponentialBackoff()
        self._listener.cancel()

        while True:
            retry = backoff.delay()
            print('PubSub Websocket closed: Retrying connection in %s seconds...', retry)

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
        self.endpoint = 'api/lobby/'

class Multiworld(BasicMultiworldClient):
    def __init__(self, guid, bot, gametype='mw'):
        self.bot = bot
        self.socket = None
        self.base_address = 'wss://mw.alttpr.com'
        self.endpoint = f'api/s1p/{guid}' if gametype == 's1p' else f'api/mw/{guid}'
