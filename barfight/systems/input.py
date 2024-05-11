from pyglet.math import Vec2
from pyglet.window import key


from .protocols import InputProtocol
from .. import ecs
from ..components import Player


class InputSystem(ecs.SystemProtocol, InputProtocol):
    def __init__(self):
        self.handler = key.KeyStateHandler()

    def process(self, *_):
        direction = Vec2()
        if self.handler[key.W]:
            direction.y += 1
        if self.handler[key.S]:
            direction.y -= 1
        if self.handler[key.A]:
            direction.x -= 1
        if self.handler[key.D]:
            direction.x += 1
        direction.normalize()

        for _, (player,) in ecs.get_components(Player):
            player.direction = direction

    def on_key_down(self, symbol: int, modifiers: int):
        if symbol == key.N:
            ecs.dispatch_event(ecs.PLAYER_ATTACK_EVENT)

    def on_key_up(self, symbol: int, modifiers: int):
        ...
