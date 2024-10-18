from math import inf
from . import BoundingBox
from pyglet.math import Vec2
from typing import Protocol, Self
from dataclasses import dataclass, field
from functools import singledispatchmethod
from __future__ import annotations


class Shape(Protocol):
    def boundary(self) -> BoundingBox: ...


@dataclass
class PointShape(Shape):
    position: Vec2 = field(default_factory=Vec2)

    def boundary(self) -> BoundingBox:
        return BoundingBox(self.position, self.position)

    @singledispatchmethod
    def overlaps(self, other) -> bool:
        raise NotImplementedError("Type not defined for argument")

    @overlaps.register
    def _(self, other: Self) -> bool:
        return self.position == other.position

    @overlaps.register
    def _(self, other: AABBShape) -> bool:
        return point_aabb_overlaps(self, other)
    
    @overlaps.register
    def _(self, other: RayShape) -> bool:
        return point_ray_overlaps(self, other)


@dataclass
class AABBShape:
    min: Vec2 = field(default_factory=Vec2)
    max: Vec2 = field(default_factory=Vec2)

    def boundary(self) -> BoundingBox:
        return BoundingBox(self.min, self.max)

    @singledispatchmethod
    def overlaps(self, other) -> bool:
        raise NotImplementedError("Type not defined for argument")

    @overlaps.register
    def _(self, other: PointShape) -> bool:
        return point_aabb_overlaps(other, self)

    @overlaps.register
    def _(self, other: Self) -> bool:
        return not (
            self.min.x >= other.max.x
            or self.max.x <= other.min.x
            or self.min.y >= other.max.y
            or self.max.y <= other.min.y
        )
    
    @overlaps.register
    def _(self, other: RayShape) -> bool:
        ...
    

@dataclass
class RayShape:
    position: Vec2 = field(default_factory=Vec2)
    direction: Vec2 = field(default_factory=Vec2)

    def boundary(self) -> BoundingBox:
        minimum = Vec2(min(self.position.x, self.direction.y), min(self.position.y, self.direction.y))
        maximum = Vec2(max(self.position.x, self.direction.y), max(self.position.y, self.direction.y))

        return BoundingBox(minimum, maximum)
    
    @singledispatchmethod
    def overlaps(self, other) -> bool:
        raise NotImplementedError("Type not defined for argument")

    @overlaps.register
    def _(self, other: AABBShape) -> bool:
        tmin = -inf
        tmax = inf

        if self.direction.x != 0:
            tx1 = (other.min.x - self.position.x) / self.direction.x
            tx2 = (other.max.x - self.position.x) / self.direction.x
            tmin = max(tmin, min(tx1, tx2))
            tmax = min(tmax, max(tx1, tx2))
        else:
            if self.position.x < other.min.x or self.position.x > other.max.x:
                return False

        if self.direction.y != 0:
            ty1 = (other.min.y - self.position.y) / self.direction.y
            ty2 = (other.max.y - self.position.y) / self.direction.y
            tmin = max(tmin, min(ty1, ty2))
            tmax = min(tmax, max(ty1, ty2))
        else:
            if self.position.y < other.min.y or self.position.y > other.max.y:
                return False

        if tmax >= tmin >= 0:
            return True
        else:
            return False
    
    @overlaps.register
    def _(self, other: PointShape) -> bool:
        return point_ray_overlaps(other, self)


def point_aabb_overlaps(point: PointShape, aabb: AABBShape) -> bool:
    return (
        aabb.min.x <= point.position.x
        and aabb.max.x <= point.position.x
        and aabb.min.y <= point.position.y
        and aabb.max.y <= point.position.y
    )


def point_ray_overlaps(point: PointShape, ray: RayShape) -> bool:
    if ray.direction.x == Vec2(0, 0):
        return False
    
    t_x = (point.position.x - ray.position.x) / ray.direction.x
    t_y = (point.position.y - ray.position.y) / ray.direction.y

    if t_x == t_y and t_x >= 0:
        return True
    
    return False
