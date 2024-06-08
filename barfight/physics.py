from dataclasses import dataclass, field
from math import inf
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

    def __post_init__(self):
        self._center = ((self.max - self.min) / 2) + self.min

    def contains_point(self, other: Point) -> bool:
        return (
            other.position.x >= self.min.x
            and other.position.y >= self.min.y
            and other.position.x <= self.max.x
            and other.position.y <= self.max.y
        )

    def contains_rect(self, other: Self) -> bool:
        return (
            other.min.x >= self.min.x
            and other.max.x <= self.max.x
            and other.min.y >= self.min.y
            and other.max.y <= self.max.y
        )

    def overlaps(self, other: Self) -> bool:
        return not (
            self.min.x > other.max.x
            or self.max.x < other.min.x
            or self.min.y > other.max.y
            or self.max.y < other.min.y
        )

    @property
    def center(self) -> Vec2:
        return self._center


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
        self.bodies: list[Body] = []

        self.is_divided = False
        self.bottom_left: QuadNode | None = None
        self.bottom_right: QuadNode | None = None
        self.top_left: QuadNode | None = None
        self.top_right: QuadNode | None = None

    def insert(self, body: Body) -> bool:
        if not self.boundary.contains_rect(body.rectangle):
            return False

        if self.depth <= 0 or (
            len(self.bodies) < self.capacity and not self.is_divided
        ):
            self.bodies.append(body)
            return True

        if not self.is_divided:
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
            self.bodies.append(body)
            return True

    def remove(self, body: Body):
        self.bodies.remove(body)
        if self.is_divided:
            self.bottom_left.remove(body)
            self.bottom_right.remove(body)
            self.top_left.remove(body)
            self.top_right.remove(body)

    def subdivide(self):
        left_x = self.boundary.min.x
        middle_x = self.boundary.min.x + (self.boundary.max.x - self.boundary.min.x) / 2
        right_x = self.boundary.max.x

        bottom_y = self.boundary.min.y
        middle_y = self.boundary.min.y + (self.boundary.max.y - self.boundary.min.y) / 2
        top_y = self.boundary.max.y

        self.bottom_left = QuadNode(
            Rectangle(Vec2(left_x, bottom_y), Vec2(middle_x, middle_y)),
            self.capacity,
            self.depth - 1,
        )
        self.bottom_right = QuadNode(
            Rectangle(Vec2(middle_x, bottom_y), Vec2(right_x, middle_y)),
            self.capacity,
            self.depth - 1,
        )
        self.top_left = QuadNode(
            Rectangle(Vec2(left_x, middle_y), Vec2(middle_x, top_y)),
            self.capacity,
            self.depth - 1,
        )
        self.top_right = QuadNode(
            Rectangle(Vec2(middle_x, middle_y), Vec2(right_x, top_y)),
            self.capacity,
            self.depth - 1,
        )

        self.is_divided = True

        current = self.bodies
        self.bodies = []
        for item in current:
            self.insert(item)

    def query(self, area: Rectangle) -> list[Body]:
        if not self.boundary.overlaps(area):
            return []

        bodies = [body for body in self.bodies if body.rectangle.overlaps(area)]

        if self.is_divided:
            bodies += (
                self.bottom_left.query(area)
                + self.bottom_right.query(area)
                + self.top_left.query(area)
                + self.top_right.query(area)
            )

        return bodies

    def _subdivisions_by_distance(self, point: Point) -> list[Self]:
        def node_distance(node: QuadNode) -> float:
            return point.position.distance(node.boundary.center)

        return sorted(
            (self.bottom_left, self.bottom_right, self.top_left, self.top_right),
            key=node_distance,
        )

    def nearest(
        self, point: Point, best_distance: float = inf, closest: Body = None
    ) -> tuple[float, Body]:
        for body in self.bodies:
            distance = point.position.distance(body.rectangle.center)
            if distance < best_distance:
                best_distance, closest = distance, body

        if self.is_divided:
            for node in self._subdivisions_by_distance(point):
                child_distance, child_body = node.nearest(point)
                if child_distance < best_distance:
                    best_distance, closest = child_distance, child_body

        return best_distance, closest


class QuadTree:
    max_depth = 8

    def __init__(self, boundary: Rectangle):
        self.boundary = boundary
        self.root: QuadNode = QuadNode(self.boundary, max_depth=self.max_depth)

    def insert(self, body: Body):
        if not self.root.insert(body):
            raise ValueError("Not within the boundary")

    def remove(self, body: Body):
        self.root.remove(body)

    def clear(self):
        self.root = QuadNode(self.boundary)

    def colliding(self): ...

    def collides_with_rect(self, rect: Rectangle): ...

    def collides_with_ray(self, ray: Ray): ...


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
