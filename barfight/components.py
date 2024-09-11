from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto

import pyglet
from pyglet.math import Vec2

from barfight.pathfinding import Cell

from .physics import Body


class ActorState(Enum):
    Idle = auto()
    Walking = auto()
    Attacking = auto()


class Layer(IntEnum):
    Game = 0
    Debug = 100


@dataclass
class Actor:
    max_speed: int
    direction: Vec2 = field(default_factory=Vec2)
    facing: float = 1
    state: ActorState = ActorState.Idle
    cooldown: float = 0


class Player: ...


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
class PhysicsBody:
    body: Body


@dataclass
class Shape:
    shape: pyglet.shapes.ShapeBase
    layer: Layer


@dataclass
class Path:
    goal: Vec2
    next_path: Vec2 | None
    path: list[Cell]


class Follow: ...
