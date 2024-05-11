from dataclasses import dataclass
from typing import Any, Protocol

import pyglet
from pyglet.math import Vec2

from .collision import AABB


class ComponentAddedProtocol(Protocol):
    def on_component_added(self, entity: int, component: Any): ...


class ComponentRemovedProtocol(Protocol):
    def on_component_removed(self, entity: int, component: Any): ...


class InputProtocol(Protocol):
    def on_key_up(self, key: int, modifiers: int): ...
    def on_key_down(self, key: int, modifiers: int): ...


class DrawProtocol(Protocol):
    def on_draw(self, window: pyglet.window.Window): ...


class ExitProtocol(Protocol):
    def on_exit(self): ...


class CollisionProtocol(Protocol):
    def on_collision(self, source: AABB, collisions: list[AABB]): ...


class PlayerStateProtocol(Protocol):
    def on_player_attack(self): ...
    def on_player_direction(self, direction: Vec2): ...
