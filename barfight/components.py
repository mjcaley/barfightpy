from dataclasses import dataclass, field
from enum import Enum, auto

import pyglet
from pyglet.math import Vec2
from pyglet.shapes import Box


class PlayerMode(Enum):
    Idle = auto()
    Attacking = auto()


class Player:
    mode: PlayerMode = PlayerMode.Idle
    expires: float = 0


class Enemy: ...


class Wall: ...


@dataclass
class Attack:
    entity: int


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


@dataclass
class BoxCollider:
    width: float
    height: float


@dataclass
class DebugCollider:
    shape: Box
