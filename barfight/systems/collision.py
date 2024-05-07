from math import inf

from pyglet.math import Vec2

from .. import ecs
from ..components import BoxCollider, Player, Position, Wall


class AABB:
    def __init__(self, entity: int, position: Position, width: float, height: float):
        self._entity = entity
        self._position = position
        self._half_width = width / 2
        self._half_height = height / 2

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

    @property
    def position(self) -> Vec2:
        return self._position

    @property
    def direction(self) -> Vec2:
        return self._direction


def point_rect_collides(point: Vec2, rect: AABB) -> bool:
    return (
        point.x >= rect.low.x
        and point.x <= rect.high.x
        and point.y >= rect.low.y
        and point.y <= rect.high.y
    )


def point_rect_resolve(point: Vec2, rect: AABB) -> Vec2:
    resolutions = [
        Vec2(rect.min_x, 0) - point,
        Vec2(rect.max_x, 0) - point,
        Vec2(0, rect.min_y) - point,
        Vec2(0, rect.max_y) - point,
    ]

    def distance(v: Vec2) -> float:
        return point.distance(v)

    nearest = min(resolutions, key=distance)

    return nearest


def rect_vs_rect(first: AABB, second: AABB) -> bool:
    return (
        first.min_x < second.max_x
        and first.max_x > second.min_x
        and first.min_y < second.max_y
        and first.max_y > second.min_y
    )


def rect_rect_resolve(first: AABB, second: AABB) -> Vec2:
    distance = inf
    nearest = Vec2(0, 0)

    left = abs(first.max_x - second.min_x)
    if left < distance:
        distance = left
        nearest = Vec2(-distance, 0)
    right = abs(first.min_x - second.max_x)
    if right < distance:
        distance = right
        nearest = Vec2(distance, 0)
    up = abs(first.min_y - second.max_y)
    if up < distance:
        distance = up
        nearest = Vec2(0, distance)
    down = abs(first.max_y - second.min_y)
    if down < distance:
        distance = down
        nearest = Vec2(0, -distance)

    return nearest


def line_vs_rect(line: Line, rect: AABB) -> float:
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


def line_rect_intersection(line: Line, t: float) -> Vec2:
    return line.position + (line.direction * t)


def distance(bodies: tuple[AABB, AABB]) -> float:
    first, second = bodies
    line = Line(
        first.position.position, first.position.position - second.position.position
    )
    t = abs(line_vs_rect(line, second))

    return t


class CollisionSystem(ecs.SystemProtocol):
    def process(self, dt: float):
        collisions = self.get_collisions()
        collisions.sort(key=distance)
        self.resolve_collisions(collisions)

    def get_collisions(self) -> list[tuple[AABB, AABB]]:
        collisions = []

        for lentity, (lpos, lcollider) in ecs.get_components(Position, BoxCollider):
            laabb = AABB(lentity, lpos, lcollider.width, lcollider.height)
            for rentity, (rpos, rcollider) in ecs.get_components(Position, BoxCollider):
                raabb = AABB(rentity, rpos, rcollider.width, rcollider.height)
                if lentity == rentity:
                    continue

                if rect_vs_rect(laabb, raabb):
                    collisions.append((laabb, raabb))

        return collisions

    def resolve_collisions(self, collisions: list[tuple[AABB, AABB]]):
        for laabb, raabb in collisions:
            if ecs.has_component(laabb.entity, Player) and ecs.has_component(
                raabb.entity, Wall
            ):
                if rect_vs_rect(laabb, raabb):
                    resolve = rect_rect_resolve(laabb, raabb)
                    laabb.position.position += resolve

                    ecs.dispatch_event(ecs.COLLISION_EVENT, laabb.entity, raabb.entity)
