from cProfile import *
from math import inf
from typing import Self

from pyglet.math import Vec2

from barfight import ecs
from barfight.components import BoxCollider, Position


class AABB:
    def __init__(self, entity: int, position: Position, width: float, height: float):
        self._entity = entity
        self._position = position
        self._half_width = width / 2
        self._half_height = height / 2

    @classmethod
    def from_entity(cls, entity: int) -> Self:
        if components := ecs.try_components(entity, Position, BoxCollider):
            position, collider = components
            return cls(entity, position, collider.width, collider.height)
        else:
            raise RuntimeError("Missing required components to create instance")

    @property
    def entity(self) -> int:
        return self._entity

    @property
    def low(self) -> Vec2:
        return Vec2(
            self.position.position.x - self._half_width,
            self.position.position.y - self._half_height,
        )

    @property
    def high(self) -> Vec2:
        return Vec2(
            self.position.position.x + self._half_width,
            self.position.position.y + self._half_height,
        )

    @property
    def position(self) -> Position:
        return self._position

    @property
    def min_x(self):
        return self.low.x

    @property
    def max_x(self):
        return self.high.x

    @property
    def min_y(self):
        return self.low.y

    @property
    def max_y(self):
        return self.high.y


class Line:
    def __init__(self, position: Vec2, direction: Vec2):
        self._position = position
        self._direction = direction.normalize()
        if direction.x == 0:
            inv_x = inf
        else:
            inv_x = 1.0 / direction.x
        if direction.y == 0:
            inv_y = inf
        else:
            inv_y = 1.0 / direction.y
        self._direction_inv = Vec2(inv_x, inv_y)

    @property
    def position(self) -> Vec2:
        return self._position

    @property
    def direction(self) -> Vec2:
        return self._direction
    
    @property
    def direction_inv(self) -> Vec2:
        return self._direction_inv




def line_vs_rect(line: Line, rect: AABB) -> float | bool:
    if line.direction.x == 0:
        t_low_x = -inf
        t_high_x = inf
    else:
        t_low_x = (rect.min_x - line.position.x) / line.direction.x
        t_high_x = (rect.max_x - line.position.x) / line.direction.x
    if line.direction.y == 0:
        t_low_y = -inf
        t_high_y = inf
    else:
        t_low_y = (rect.min_y - line.position.y) / line.direction.y
        t_high_y = (rect.max_y - line.position.y) / line.direction.y

    t_close_x = min(t_low_x, t_high_x)
    t_far_x = max(t_low_x, t_high_x)
    t_close_y = min(t_low_y, t_high_y)
    t_far_y = max(t_low_y, t_high_y)

    t_close = max(t_close_x, t_close_y)
    t_far = min(t_far_x, t_far_y)

    if t_close > t_far:
        return False

    return t_close


def line_vs_rect2(line: Line, rect: AABB) -> float | None:
    # https://tavianator.com/2022/ray_box_boundary.html
    tmin = 0.0
    tmax = inf

    t1_x = (rect.min_x - line.position.x) * line.direction_inv.x
    t2_x = (rect.max_x - line.position.x) * line.direction_inv.x
    tmin = min(max(t1_x, tmin), max(t2_x, tmin))
    tmax = max(min(t1_x, tmax), min(t2_x, tmax))

    t1_y = (rect.min_y - line.position.y) * line.direction_inv.y
    t2_y = (rect.max_y - line.position.y) * line.direction_inv.y
    tmin = min(max(t1_y, tmin), max(t2_y, tmin))
    tmax = max(min(t1_y, tmax), min(t2_y, tmax))

    return tmin if tmax > max(tmin, 0.0) else None


run()
