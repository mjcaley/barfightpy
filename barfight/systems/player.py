from loguru import logger
from pyglet.math import Vec2

from .. import ecs
from ..components import (Attack, BoxCollider, Player, PlayerState, Position,
                          Velocity)
from .protocols import PlayerStateProtocol


class PlayerSystem(ecs.SystemProtocol, PlayerStateProtocol):
    def process(self, dt: float):
        for entity, (player, position, velocity) in ecs.get_components(Player, Position, Velocity):
            match player.state:
                case PlayerState.Idle:
                    self.idle(entity, player, position, velocity)
                case PlayerState.Walking:
                    self.walking(entity, player, position, velocity)
                case PlayerState.Attacking:
                    self.attacking(dt, entity, player, position, velocity)

    def idle(self, entity: int, player: Player, position: Position, velocity: Velocity):
        match player.direction:
            case Vec2(0, 0): ...
            case direction:
                player.state = PlayerState.Walking
                velocity.direction = direction
                velocity.speed = player.max_speed

    def walking(self, entity: int, player: Player, position: Position, velocity: Velocity):
        match player.direction:
            case Vec2(0, 0):
                player.state = PlayerState.Idle
                velocity.direction = player.direction
                velocity.speed = 0
            case _:
                velocity.direction = player.direction

    def attacking(self, dt: float, entity: int, player: Player, position: Position, velocity: Velocity):
        match player.cooldown, player.direction:
            case cooldown, _ if cooldown > 0:
                player.cooldown = max(0, player.cooldown - dt)
            case 0, Vec2(0, 0):
                player.state = PlayerState.Idle
                velocity.direction = player.direction
                velocity.speed = 0
            case 0, _:
                player.state = PlayerState.Walking
                velocity.direction = player.direction
                velocity.speed = player.max_speed

    def on_player_attack(self):
        for entity, (player, position, velocity) in ecs.get_components(Player, Position, Velocity):
            match player.state, player.cooldown:
                case PlayerState.Idle | PlayerState.Walking, _:
                    player.state = PlayerState.Attacking
                    velocity.speed = 0
                    player.cooldown = 0.2
                    ecs.create_entity(
                        Attack(entity),
                        Position(
                            Vec2(position.position.x + 50, position.position.y)
                        ),  # Position based off player's collider
                        BoxCollider(20, 20),
                    )
                case PlayerState.Attacking, 0:
                    player.cooldown = 0.2
                    ecs.create_entity(
                        Attack(entity),
                        Position(
                            Vec2(position.position.x + 50, position.position.y)
                        ),  # Position based off player's collider
                        BoxCollider(20, 20),
                    )
