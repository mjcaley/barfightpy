from typing import Any, Protocol

from pyglet.math import Vec2
from pyglet.window import Window

COMPONENT_ADDED_EVENT = "component_added"
COMPONENT_REMOVED_EVENT = "component_removed"
DRAW_EVENT = "draw"
KEY_UP_EVENT = "key_up"
KEY_DOWN_EVENT = "key_down"
EXIT_EVENT = "exit"
COLLISION_EVENT = "collision"
DAMAGE_EVENT = "damage"
PLAYER_DIRECTION_EVENT = "player_direction"
PLAYER_ATTACK_EVENT = "player_attack"


class ComponentAddedProtocol(Protocol):
    def on_component_added(self, entity: int, component: Any): ...


class ComponentRemovedProtocol(Protocol):
    def on_component_removed(self, entity: int, component: Any): ...


class InputProtocol(Protocol):
    def on_key_up(self, key: int, modifiers: int): ...
    def on_key_down(self, key: int, modifiers: int): ...


class DrawProtocol(Protocol):
    def on_draw(self, window: Window): ...


class ExitProtocol(Protocol):
    def on_exit(self): ...


class CollisionProtocol(Protocol):
    def on_collision(self, source: int, collisions: set[int]): ...


class PlayerStateProtocol(Protocol):
    def on_player_attack(self): ...
    def on_player_direction(self, direction: Vec2): ...
