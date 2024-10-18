from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import partial
from math import inf
from typing import Any, Self

from pyglet.math import Vec2


@dataclass
class Point:
    position: Vec2 = field(default_factory=Vec2)
    layer: int = 0b1
    mask: int = 0b1111111111111111


@dataclass
class Rectangle:
    min: Vec2 = field(default_factory=Vec2)
    max: Vec2 = field(default_factory=Vec2)

    def __hash__(self):
        return hash(self.min.x) + hash(self.min.y) + hash(self.max.x) + hash(self.max.y)

    @classmethod
    def from_dimensions(cls, position: Vec2, width: float, height: float) -> Self:
        return cls(
            Vec2(position.x - width / 2, position.y - height / 2),
            Vec2(position.x + width / 2, position.y + height / 2),
        )

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
            self.min.x >= other.max.x
            or self.max.x <= other.min.x
            or self.min.y >= other.max.y
            or self.max.y <= other.min.y
        )

    @property
    def center(self) -> Vec2:
        return ((self.max - self.min) / 2) + self.min

    @center.setter
    def center(self, position: Vec2):
        direction = position - self.center
        self.min += direction
        self.max += direction

    @property
    def width(self) -> float:
        return self.max.x - self.min.x

    @property
    def height(self) -> float:
        return self.max.y - self.min.y


@dataclass
class Ray:
    position: Vec2 = field(default_factory=Vec2)
    direction: Vec2 = field(default_factory=Vec2)
    layer: int = 0b1
    mask: int = 0b1111111111111111

    def intersects(self, rect: Rectangle) -> Vec2 | None:
        tmin = -inf
        tmax = inf

        if self.direction.x != 0:
            tx1 = (rect.min.x - self.position.x) / self.direction.x
            tx2 = (rect.max.x - self.position.x) / self.direction.x
            tmin = max(tmin, min(tx1, tx2))
            tmax = min(tmax, max(tx1, tx2))
        else:
            if self.position.x < rect.min.x or self.position.x > rect.max.x:
                return None

        if self.direction.y != 0:
            ty1 = (rect.min.y - self.position.y) / self.direction.y
            ty2 = (rect.max.y - self.position.y) / self.direction.y
            tmin = max(tmin, min(ty1, ty2))
            tmax = min(tmax, max(ty1, ty2))
        else:
            if self.position.y < rect.min.y or self.position.y > rect.max.y:
                return None

        if tmax >= tmin >= 0:
            intersection = self.position + (self.direction * tmin)
            return intersection
        else:
            return None

    def distance(self, point: Vec2, rect: Rectangle) -> float | None:
        if intersection := self.intersects(rect):
            return intersection.distance(point)
        else:
            return inf


class BodyKind(Enum):
    Static = auto()
    Dynamic = auto()
    Sensor = auto()


@dataclass
class Body:
    rectangle: Rectangle
    kind: BodyKind = BodyKind.Dynamic
    layer: int = 0b1
    mask: int = 0b1111111111111111
    data: Any = None

    def __hash__(self):
        return hash(id(self))

    def resolve_with(self, other: Self) -> Vec2:
        distance = inf
        nearest = Vec2(0, 0)

        left = abs(self.rectangle.max.x - other.rectangle.min.x)
        if left < distance:
            distance = left
            nearest = Vec2(-distance, 0)
        right = abs(self.rectangle.min.x - other.rectangle.max.x)
        if right < distance:
            distance = right
            nearest = Vec2(distance, 0)
        up = abs(self.rectangle.min.y - other.rectangle.max.y)
        if up < distance:
            distance = up
            nearest = Vec2(0, distance)
        down = abs(self.rectangle.max.y - other.rectangle.min.y)
        if down < distance:
            distance = down
            nearest = Vec2(0, -distance)

        self.rectangle.center += nearest


class QuadTree:
    def __init__(self, boundary: Rectangle, capacity: int, max_depth: int = 8):
        self.boundary = boundary
        self.capacity = capacity
        self.depth = max_depth
        self.bodies: list[Body] = []

        self.is_divided = False
        self.bottom_left: QuadTree | None = None
        self.bottom_right: QuadTree | None = None
        self.top_left: QuadTree | None = None
        self.top_right: QuadTree | None = None

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

            if not all(
                self.bottom_left.bodies,
                self.bottom_right.bodies,
                self.top_left.bodies,
                self.top_right.bodies,
            ):
                self.bottom_left = self.bottom_right = self.top_left = (
                    self.top_right
                ) = None
                self.is_divided = False

    def subdivide(self):
        left_x = self.boundary.min.x
        middle_x = self.boundary.min.x + (self.boundary.max.x - self.boundary.min.x) / 2
        right_x = self.boundary.max.x

        bottom_y = self.boundary.min.y
        middle_y = self.boundary.min.y + (self.boundary.max.y - self.boundary.min.y) / 2
        top_y = self.boundary.max.y

        self.bottom_left = QuadTree(
            Rectangle(Vec2(left_x, bottom_y), Vec2(middle_x, middle_y)),
            self.capacity,
            self.depth - 1,
        )
        self.bottom_right = QuadTree(
            Rectangle(Vec2(middle_x, bottom_y), Vec2(right_x, middle_y)),
            self.capacity,
            self.depth - 1,
        )
        self.top_left = QuadTree(
            Rectangle(Vec2(left_x, middle_y), Vec2(middle_x, top_y)),
            self.capacity,
            self.depth - 1,
        )
        self.top_right = QuadTree(
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
        def node_distance(node: QuadTree) -> float:
            return point.position.distance(node.boundary.center)

        return sorted(
            (self.bottom_left, self.bottom_right, self.top_left, self.top_right),
            key=node_distance,
        )

    def nearest(
        self, point: Point, best_distance: float = inf, closest: Body | None = None
    ) -> tuple[float, Body]:
        for body in self.bodies:
            if point.layer & body.mask == 0 and body.layer & point.mask == 0:
                continue
            distance = point.position.distance(body.rectangle.center)
            if distance < best_distance:
                best_distance, closest = distance, body

        if self.is_divided:
            for node in self._subdivisions_by_distance(point):
                child_distance, child_body = node.nearest(point)
                if child_distance < best_distance:
                    best_distance, closest = child_distance, child_body

        return best_distance, closest

    def collisions(self, parent_bodies: list[Body]) -> list[tuple[Body, Body]]:
        colliding = []
        bodies = self.bodies + parent_bodies

        for first_body in bodies:
            for second_body in bodies:
                if first_body is second_body:
                    continue
                if not self.boundary.overlaps(
                    first_body.rectangle
                ) or not self.boundary.overlaps(second_body.rectangle):
                    continue
                if first_body.rectangle.overlaps(second_body.rectangle):
                    colliding.append((first_body, second_body))

        if self.is_divided:
            colliding += (
                self.bottom_left.collisions(bodies)
                + self.bottom_right.collisions(bodies)
                + self.top_left.collisions(bodies)
                + self.top_right.collisions(bodies)
            )

        return colliding


def closest_body(point: Vec2, body: Body) -> float:
    return body.rectangle.center.distance(point)


@dataclass
class Arbiter:
    first_body: Body
    second_body: Body
    is_first_collision: bool = False


class PhysicsWorld:
    def __init__(self, min: Vec2, max: Vec2, max_depth=8):
        self.min = min
        self.max = max
        self.max_depth = max_depth
        self.root = QuadTree(Rectangle(self.min, self.max), self.max_depth)
        self.active_collisions: set[tuple[Body, Body]] = set()
        self.position_change_callback = None
        self.on_collision_callback = None
        self.on_sensor_callback = None

    @property
    def boundary(self) -> Rectangle:
        return self.root.boundary

    def insert(self, body: Body):
        if not self.root.insert(body):
            raise ValueError("Not within the boundary")

    def remove(self, body: Body):
        self.root.remove(body)

    def clear(self):
        self.root = QuadTree(Rectangle(self.min, self.max), self.max_depth)

    def collisions(self) -> list[tuple[Body, Body]]:
        return self.root.collisions([])

    def _call_position_change(self, body: Body):
        if self.position_change_callback:
            self.position_change_callback(body)

    def _call_on_collision(self, arbiter: Arbiter):
        if self.on_collision_callback:
            self.on_collision_callback(arbiter)

    def _call_on_sensor(self, arbiter: Arbiter):
        if self.on_sensor_callback:
            self.on_sensor_callback(arbiter)

    def resolve(self, target: Body, collisions: set[Body]):
        for body in sorted(
            collisions, key=partial(closest_body, target.rectangle.center)
        ):
            if target.layer & body.mask == 0 and body.layer and target.mask == 0:
                continue

            arbiter = Arbiter(
                target, body, (target, body) not in self.active_collisions
            )

            match body.kind:
                case BodyKind.Sensor:
                    self._call_on_sensor(arbiter)
                case BodyKind.Static:
                    if target.rectangle.overlaps(body.rectangle):
                        target.resolve_with(body)
                        self._call_position_change(target)
                        self._call_on_collision(arbiter)

    def step(self):
        new_collisions = self.collisions()

        colliding: dict[Body, set[Body]] = defaultdict(set)
        for first, second in new_collisions:
            colliding[first].add(second)
            colliding[second].add(first)
        for target, collisions in colliding.items():
            self.resolve(target, collisions)

        self.active_collisions = new_collisions

    def query(self, area: Rectangle) -> list[Body]:
        return self.root.query(area)

    def query_with(self, area: Rectangle, layer: int) -> list[Body]:
        bodies = self.query(area)
        return [body for body in bodies if body.mask & layer != 0]

    def is_colliding(self, area: Rectangle) -> bool:
        return self.query(area) != []

    def is_colliding_with(self, area: Rectangle, layer: int) -> bool:
        return self.query_with(area, layer) != []

    def nearest(self, point: Point):
        return self.root.nearest(point)
