from typing import Any, Protocol, runtime_checkable

from pyglet.math import Vec2
from pyglet.window import Window

from .physics import Arbiter

COMPONENT_ADDED_EVENT = "component_added"
COMPONENT_REMOVED_EVENT = "component_removed"
DRAW_EVENT = "draw"
KEY_UP_EVENT = "key_up"
KEY_DOWN_EVENT = "key_down"
MOUSE_DOWN_EVENT = "mouse_down"
MOUSE_UP_EVENT = "mouse_up"
EXIT_EVENT = "exit"
COLLISION_EVENT = "collision"
SENSOR_EVENT = "sensor"
POSITION_CHANGED_EVENT = "position_changed"
DAMAGE_EVENT = "damage"
PLAYER_DIRECTION_EVENT = "player_direction"
PLAYER_ATTACK_EVENT = "player_attack"
AI_DIRECTION_EVENT = "ai_direction"
AI_ATTACK_EVENT = "ai_attack"


@runtime_checkable
class ComponentAddedProtocol(Protocol):
    def on_component_added(self, source: int, component: Any): ...


@runtime_checkable
class ComponentRemovedProtocol(Protocol):
    def on_component_removed(self, source: int, component: Any): ...


@runtime_checkable
class InputProtocol(Protocol):
    def on_key_up(self, symbol: int, modifiers: int): ...
    def on_key_down(self, symbol: int, modifiers: int): ...
    def on_mouse_down(self, x: int, y: int, button: int, modifiers: int): ...
    def on_mouse_up(self, x: int, y: int, button: int, modifiers: int): ...


@runtime_checkable
class DrawProtocol(Protocol):
    def on_draw(self, window: Window): ...


@runtime_checkable
class ExitProtocol(Protocol):
    def on_exit(self): ...


@runtime_checkable
class CollisionProtocol(Protocol):
    def on_collision(self, arbiter: Arbiter): ...
    def on_sensor(self, arbiter: Arbiter): ...


@runtime_checkable
class PlayerStateProtocol(Protocol):
    def on_player_attack(self): ...
    def on_player_direction(self, direction: Vec2): ...


@runtime_checkable
class AIStateProtocol(Protocol):
    def on_ai_attack(self, target: int): ...
    def on_ai_direction(self, target: int, direction: Vec2): ...


@runtime_checkable
class PositionChangedProtocol(Protocol):
    def on_position_changed(self, source: int): ...
