from dataclasses import dataclass, field
from typing import Any, Self
from pyglet.math import Vec2


@dataclass
class Point:
    position: Vec2 = field(default_factory=Vec2)
    layer: int = 0b0
    mask: int = 0b0


@dataclass
class Rectangle:
    min: Vec2 = field(default_factory=Vec2)
    max: Vec2 = field(default_factory=lambda: Vec2(1, 1))
    layer: int = 0b0
    mask: int = 0b0
    data: Any = None

    def contains_point(self, other: Point) -> bool:
        return other >= self.min and other <= self.max

    def contains_rect(self, other: Self) -> bool:
        return other.min >= self.min and other.max <= self.max
    
    def overlaps(self, other: Self) -> bool:
        return (
        self.min.x < other.max.x
        and self.max.x > other.min.x
        and self.min.y < other.max.y
        and self.max.y > other.min.y
    )


@dataclass
class Ray:
    position: Vec2 = field(default_factory=Vec2)
    direction: Vec2 = field(default_factory=Vec2)
    layer: int = 0b0
    mask: int = 0b0



class QuadTree:
    max_depth = 8

    def __init__(self, size: Rectangle = None, depth: int = 0):
        self.size = size or Rectangle()
        self.depth = depth
        self.items: list[Rectangle] = []
        self.children: tuple[Rectangle | None] = (None, None, None, None)

    def clear(self):
        ...


class World:
    def __init__(self, size: Vec2):
        self.size = size
        self.bodies = []

    


# World class
# world size?
# manages bodies
# performs step to run collision detection and resolution
#   keeps cache of active collisions
# callbacks
#   collision -> Arbiter
# performs queries
#   ray -> tuple[AABB]
#   objects near pos, within rect -> tuple[AABB]


# AABB - only body type currently
# position
# length, width
# user data (e.g. entity id)
# contains
# overlap
# layer
# mask

# Ray
# position
# direction
