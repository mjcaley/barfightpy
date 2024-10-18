from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any
from pyglet.math import Vec2
from .shapes import Shape


ALL_BODIES = 0b1111111111111111


class BodyKind(Enum):
    Static = auto()
    Dynamic = auto()
    Sensor = auto()


@dataclass
class Body:
    shape: Shape
    kind: BodyKind = BodyKind.Dynamic
    velocity: Vec2 = field(default_factory=Vec2)
    layer: int = 0b1
    mask: int = ALL_BODIES
    data: Any = None

    def __hash__(self):
        return hash(id(self))
