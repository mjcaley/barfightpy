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
    max: Vec2 = field(default_factory=Vec2)

    def contains_point(self, other: Point) -> bool:
        return other.x >= self.min.x and other.y >= self.min.y and other.x <= self.max.x and other.y <= self.max.y

    def contains_rect(self, other: Self) -> bool:
        return other.min.x >= self.min.x and other.max.x <= self.max.x and other.min.y >= self.min.y and other.max.y <= self.max.y
    
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


@dataclass
class Body:
    rectangle: Rectangle
    layer: int = 0b0
    mask: int = 0b0
    data: Any = None


class QuadNode:
    def __init__(self, boundary: Rectangle, capacity: int, max_depth: int = 8):
        self.boundary = boundary
        self.capacity = capacity
        self.depth = max_depth
        self.items: list[Body] = []

        self.is_divided = False
        self.bottom_left: QuadNode | None = None
        self.bottom_right: QuadNode | None = None
        self.top_left: QuadNode | None = None
        self.top_right: QuadNode | None = None

    def insert(self, body: Body) -> bool:
        if not self.boundary.contains_rect(body.rectangle):
            return False
        
        if self.depth <= 0 or len(self.items) < self.capacity and not self.is_divided:
            self.items.append(body)
            return True
        
        self.subdivide()
        
        if self.bottom_left.insert(body):
            return True
        elif self.bottom_right.insert(body):
            return True
        elif self.top_left.insert(body):
            return True
        elif self.top_right.insert(body):
            return True
        else:
            self.items.append(body)
            return True

    def subdivide(self):
        left_x = self.boundary.min.x
        middle_x = self.boundary.min.x + (self.boundary.max.x - self.boundary.min.x) / 2
        right_x = self.boundary.max.x

        bottom_y = self.boundary.min.y
        middle_y = self.boundary.min.y + (self.boundary.max.y - self.boundary.min.y) / 2
        top_y = self.boundary.max.y

        self.bottom_left = QuadNode(Rectangle(Vec2(left_x, bottom_y), Vec2(middle_x, middle_y)), self.capacity, self.depth - 1)
        self.bottom_right = QuadNode(Rectangle(Vec2(middle_x, bottom_y), Vec2(right_x, middle_y)), self.capacity, self.depth - 1)
        self.top_left = QuadNode(Rectangle(Vec2(left_x, middle_y), Vec2(middle_x, top_y)), self.capacity, self.depth - 1)
        self.top_right = QuadNode(Rectangle(Vec2(middle_x, middle_y), Vec2(right_x, top_y)), self.capacity, self.depth - 1)
        
        self.is_divided = True

        current = self.items
        self.items = []
        for item in current:
            self.insert(item)


class QuadTree:
    max_depth = 8

    def __init__(self, boundary: Rectangle):
        self.boundary = boundary
        self.root: QuadNode = QuadNode(self.boundary)

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
