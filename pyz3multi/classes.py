import uuid
import pyz3multi.websocket

class Game:
    '''Class for describing a game'''
    def __init__(self, name: str, description: str, has_password: bool, game: str, world_count: int, client: pyz3multi.websocket.Game=None):
        self.name = name
        self.description = description
        self.has_password = has_password
        self.game = game
        self.world_count = world_count
        self.client = client

    def __str__(self):
        return self.game

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'name={self.name!r}, game={self.game!r})')