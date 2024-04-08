from pyglet.math import Vec2
from pyglet.window import key

from .. import ecs
from ..components import Player, Velocity


class InputSystem(ecs.SystemProtocol):
    def __init__(self):
        self.handler = key.KeyStateHandler()

    def process(self, *_):
        for _, (_, velocity) in ecs.get_components(Player, Velocity):
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
            velocity.direction = direction
