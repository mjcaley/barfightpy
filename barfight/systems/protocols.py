from typing import Any, Protocol

import pyglet

from .collision import AABB


class ComponentAddedProtocol(Protocol):
    def on_component_added(self, entity: int, component: Any): ...


class ComponentRemovedProtocol(Protocol):
    def on_component_removed(self, entity: int, component: Any): ...


class DrawProtocol(Protocol):
    def on_draw(self, window: pyglet.window.Window): ...


class ExitProtocol(Protocol):
    def on_exit(self): ...


class CollisionProtocol(Protocol):
    def on_collision(self, source: AABB, collisions: list[AABB]): ...
