from dataclasses import dataclass, field

import pyglet
from pyglet.math import Vec2


class Player: ...


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
