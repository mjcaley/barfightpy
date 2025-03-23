from dataclasses import dataclass, field
from functools import singledispatchmethod
from itertools import chain, islice, pairwise
from math import cos, inf, pi, radians, sin
from typing import Any, Generator, Self

from pyglet.math import Vec2


@dataclass(frozen=True)
class Collision:
    penetration: Vec2
    depth: float


@dataclass(frozen=True)
class TimeOfImpact:
    impact_time: float
    penetration: Vec2
    depth: float


@dataclass
class Point:
    point: Vec2 = field(default_factory=Vec2)

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Collision | None:
        raise NotImplementedError

    @property
    def center(self) -> Vec2:
        return self.point
    
    @center.setter
    def center(self, value: Vec2):
        self.point = value

    def furthest(self, direction: Vec2) -> Vec2:
        return self.point


@dataclass
class Line:
    base: Vec2 = field(default_factory=Vec2)
    direction: Vec2 = field(default_factory=Vec2)

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Collision | None:
        raise NotImplementedError

    @property
    def center(self) -> Vec2:
        return self.base


@dataclass
class LineSegment:
    point1: Vec2 = field(default_factory=Vec2)
    point2: Vec2 = field(default_factory=Vec2)

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Collision | None:
        raise NotImplementedError

    def edges(self) -> Generator[Self, None, None]:
        yield self

    @property
    def center(self) -> Vec2:
        return (self.point1 + self.point2) / 2

    def furthest(self, direction: Vec2) -> Vec2:
        if self.point1.dot(direction) > self.point1.dot(direction):
            return self.point1
        else:
            return self.point2


@dataclass
class Circle:
    center: Vec2 = field(default_factory=Vec2)
    radius: float = 0

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Collision | None:
        raise NotImplementedError

    @singledispatchmethod
    def minkowski_difference(self, any) -> Any:
        raise NotImplementedError

    def vertices(self, num_points=16) -> Generator[Vec2, None, None]:
        point = self.center + Vec2(self.radius, 0)
        rotation = 2 * pi / num_points
        for _ in range(num_points):
            point = point.rotate(rotation)
            yield point

    def furthest(self, direction: Vec2) -> Vec2:
        return self.center + self.radius * direction.normalize()


@dataclass
class Rectangle:
    origin: Vec2 = field(default_factory=Vec2)
    size: Vec2 = field(default_factory=Vec2)

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Collision | None:
        raise NotImplementedError

    @singledispatchmethod
    def minkowski_difference(self, any) -> Any:
        raise NotImplementedError

    @property
    def center(self) -> Vec2:
        return self.origin + (self.size / 2)

    @center.setter
    def center(self, value: Vec2):
        self.origin = value - (self.size / 2)

    @property
    def bottom_left_vertex(self) -> Vec2:
        return self.origin

    @property
    def bottom_right_vertex(self) -> Vec2:
        return Vec2(self.origin.x + self.size.x, self.origin.y)

    @property
    def top_left_vertex(self) -> Vec2:
        return Vec2(self.origin.x, self.origin.y + self.size.y)

    @property
    def top_right_vertex(self) -> Vec2:
        return self.origin + self.size

    def vertices(self) -> Generator[Vec2, None, None]:
        yield self.bottom_left_vertex
        yield self.top_left_vertex
        yield self.top_right_vertex
        yield self.bottom_right_vertex

    def edges(self) -> Generator[LineSegment, None, None]:
        for v1, v2 in pairwise(chain(self.vertices(), islice(self.vertices(), 1))):
            yield LineSegment(v1, v2)

    def axes(self) -> Generator[Vec2, None, None]:
        yield Vec2(1, 0)
        yield Vec2(0, 1)

    def furthest(self, direction: Vec2) -> Vec2:
        match direction.normalize():
            case Vec2(x, y) if x == 0 and y == 0:
                raise ValueError("Direction vector cannot be 0, 0")
            case Vec2(x, y) if x <= 0 and y <= 0:
                return self.bottom_left_vertex
            case Vec2(x, y) if x <= 0 and y >= 0:
                return self.top_left_vertex
            case Vec2(x, y) if x >= 0 and y >= 0:
                return self.top_right_vertex
            case Vec2(x, y) if x >= 0 and y <= 0:
                return self.bottom_right_vertex
            case _:
                raise ValueError("Direction must not be zero")


@dataclass
class OrientedRectangle:
    center: Vec2 = field(default_factory=Vec2)
    half_extent: Vec2 = field(default_factory=Vec2)
    rotation: float = 0

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Collision | None:
        raise NotImplementedError

    @singledispatchmethod
    def minkowski_difference(self, any) -> Any:
        raise NotImplementedError

    @property
    def top_right_vertex(self) -> Vec2:
        vertex = self.half_extent.rotate(self.rotation) + self.center

        return vertex

    @property
    def bottom_right_vertex(self) -> Vec2:
        vertex = Vec2(self.half_extent.x * -1, self.half_extent.y)
        vertex = vertex.rotate(self.rotation) + self.center

        return vertex

    @property
    def bottom_left_vertex(self) -> Vec2:
        vertex = Vec2(self.half_extent.x, self.half_extent.y) * -1
        vertex = vertex.rotate(self.rotation) + self.center

        return vertex

    @property
    def top_left_vertex(self) -> Vec2:
        vertex = Vec2(self.half_extent.x, self.half_extent.y * -1)
        vertex = vertex.rotate(self.rotation) + self.center

        return vertex

    def vertices(self) -> Generator[Vec2, None, None]:
        yield self.bottom_left_vertex
        yield self.top_left_vertex
        yield self.top_right_vertex
        yield self.bottom_right_vertex

    def edges(self) -> Generator[LineSegment, None, None]:
        for v1, v2 in pairwise(chain(self.vertices(), islice(self.vertices(), 1))):
            yield LineSegment(v1, v2)

    def axes(self) -> Generator[Vec2, None, None]:
        yield Vec2(cos(self.rotation), sin(self.rotation))
        yield Vec2(cos(self.rotation + radians(90)), sin(self.rotation + radians(90)))

    @property
    def bounding_box(self) -> Rectangle:
        min_x = inf
        max_x = -inf
        min_y = inf
        max_y = -inf
        for vertex in self.vertices():
            min_x = min(min_x, vertex.x)
            max_x = max(max_x, vertex.x)
            min_y = min(min_y, vertex.y)
            max_y = max(max_y, vertex.y)

        return Rectangle(Vec2(min_x, min_y), Vec2(max_x - min_x, max_y - min_y))

    def furthest(self, direction: Vec2) -> Vec2:
        if direction == Vec2(0, 0):
            raise ValueError("Direction vector cannot be 0, 0")
        furthest_distance = -inf
        furthest_vertex = self.center

        for vertex in self.vertices():
            distance = vertex.dot(direction)
            if distance > furthest_distance:
                furthest_distance = distance
                furthest_vertex = vertex

        return furthest_vertex


@dataclass
class Polygon:
    points: list[Vec2]

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Collision | None:
        raise NotImplementedError

    @singledispatchmethod
    def minkowski_difference(self, any) -> Any:
        raise NotImplementedError

    def vertices(self) -> Generator[Vec2, None, None]:
        return (point for point in self.points)

    def edges(self) -> Generator[LineSegment, None, None]:
        for v1, v2 in pairwise(chain(self.vertices(), islice(self.vertices(), 1))):
            yield LineSegment(v1, v2)

    def axes(self) -> Generator[Vec2, None, None]:
        for edge in self.edges():
            yield (edge.point2 - edge.point1).rotate90().normalize()

    @property
    def center(self) -> Vec2:
        return self.bounding_box.center

    @center.setter
    def center(self, value: Vec2):
        self.points = [point + value for point in self.points]

    @property
    def bounding_box(self) -> Rectangle:
        min_x = inf
        max_x = -inf
        min_y = inf
        max_y = -inf

        for vertex in self.vertices():
            min_x = min(min_x, vertex.x)
            max_x = max(max_x, vertex.x)
            min_y = min(min_y, vertex.y)
            max_y = max(max_y, vertex.y)

        return Rectangle(Vec2(min_x, min_y), Vec2(max_x - min_x, max_y - min_y))

    def furthest(self, direction: Vec2) -> Vec2:
        furthest_distance = -inf
        furthest_vertex = self.center

        for vertex in self.vertices():
            distance = vertex.dot(direction)
            if distance > furthest_distance:
                furthest_distance = distance
                furthest_vertex = vertex

        return furthest_vertex

    def is_convex(self) -> bool:
        cross = []

        for e1, e2 in pairwise(chain(self.edges(), islice(self.edges(), 1))):
            v1 = e1.point2 - e1.point1
            v2 = e2.point2 - e2.point1
            cross.append(v1.x * v2.y - v1.y * v2.x)

        all_positive = all(c >= 0 for c in cross)
        all_negative = all(c <= 0 for c in cross)

        return all_positive != all_negative
