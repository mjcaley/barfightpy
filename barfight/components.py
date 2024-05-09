from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto

import pyglet
from pyglet.math import Vec2


class PlayerMode(Enum):
    Idle = auto()
    Attacking = auto()


class Layer(IntEnum):
    Game = 0
    Debug = 100


class Player:
    mode: PlayerMode = PlayerMode.Idle
    expires: float = 0


class Enemy: ...


class Wall: ...


@dataclass
class Attack:
    entity: int
    cleanup: bool = False


@dataclass
class Health:
    current: int
    maximum: int


@dataclass
class Velocity:
    direction: Vec2 = field(default_factory=Vec2)
    speed: float = 0


@dataclass
class Position:
    position: Vec2 = field(default_factory=Vec2)


@dataclass
class Sprite:
    sprite: pyglet.sprite.Sprite
    layer: Layer


@dataclass
class BoxCollider:
    width: float
    height: float


@dataclass
class Shape:
    shape: pyglet.shapes.ShapeBase
    layer: Layer
