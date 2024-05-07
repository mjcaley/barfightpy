from pyglet.math import Vec2
from pyglet.window import key

from .. import ecs
from ..components import (Attack, BoxCollider, Player, PlayerMode, Position,
                          Velocity)


class InputSystem(ecs.SystemProtocol):
    def __init__(self):
        self.handler = key.KeyStateHandler()

    def process(self, *_):
        for entity, (player, position, velocity) in ecs.get_components(
            Player, Position, Velocity
        ):
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

            if self.handler[key.N] and player.mode != PlayerMode.Attacking:
                player.mode = PlayerMode.Attacking
                player.expires = 0.2
                ecs.create_entity(
                    Attack(entity),
                    Position(
                        Vec2(position.position.x + 50, position.position.y)
                    ),  # Position based off player's collider
                    BoxCollider(20, 20),
                )
