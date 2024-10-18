from dataclasses import dataclass, field
from typing import Self
from pyglet.math import Vec2
from .body import Body
from .shapes import PointShape, AABBShape, RayShape


@dataclass
class BoundingBox:
    min: Vec2 = field(default_factory=Vec2)
    max: Vec2 = field(default_factory=Vec2)

    def overlaps(self, other: Self) -> bool:
        return not (
            self.min.x >= other.max.x
            or self.max.x <= other.min.x
            or self.min.y >= other.max.y
            or self.max.y <= other.min.y
        )


@dataclass
class Arbiter:
    first_body: Body
    second_body: Body
    is_first_collision: bool = False
