from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from pyglet.math import Vec2

from .shapes import Shape


class BodyKind(Enum):
    Static = auto()
    Dynamic = auto()
    Sensor = auto()


@dataclass
class Body:
    shape: Shape
    kind: BodyKind = BodyKind.Dynamic
    velocity: Vec2 = field(default_factory=Vec2)
    data: Any = None

    def __hash__(self):
        return hash(id(self))
