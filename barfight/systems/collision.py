from dataclasses import dataclass
import esper
from loguru import logger
from pyglet.math import Vec2

from .. import ecs
from ..components import BoxCollider, Player, Position, Velocity, Wall


# Reference
# - https://blog.hamaluik.ca/posts/simple-aabb-collision-using-minkowski-difference/
# - https://blog.hamaluik.ca/posts/swept-aabb-collision-using-minkowski-difference/

@dataclass
class AABB:
    center: Vec2
    extents: Vec2

    @property
    def min(self) -> Vec2:
        return Vec2(self.center.x - self.extents.x, self.center.y - self.extents.y)
    
    @property
    def max(self) -> Vec2:
        return Vec2(self.center.x + self.extents.x, self.center.y + self.extents.y)
    
    @property
    def size(self) -> Vec2:
        return Vec2(self.extents.x * 2, self.extents.y * 2)
    
    def minkowski_difference(self, other: "AABB") -> "AABB":
        top_left = self.min - other.max
        full_size = self.size + other.size

        return AABB(top_left + (full_size / 2), full_size / 2)

    def closest_point_on_bounds_to_point(self, point: Vec2) -> Vec2:
        min_distance = abs(point.x - self.min.x)
        bounds_point = Vec2(self.min.x, point.y)

        if abs(self.max.x - point.x) < min_distance:
            min_distance = abs(self.max.x - point.x)
            bounds_point = Vec2(self.max.x, point.y)
        if abs(self.max.y - point.y) < min_distance:
            min_distance = abs(self.max.y - point.y)
            bounds_point = Vec2(point.x, self.max.y)
        if abs(self.min.y - point.y) < min_distance:
            min_distance = abs(self.min.y - point.y)
            bounds_point = Vec2(point.x, self.min.y)
        
        return bounds_point


@dataclass
class Hit:
    source: int
    target: int
    resolve: Vec2


class CollisionSystem(ecs.SystemProtocol):
    def process(self, dt: float):
        for lentity, (lposition, lcollider) in ecs.get_components(
            Position, BoxCollider
        ):
            for rentity, (rposition, rcollider) in ecs.get_components(
                Position, BoxCollider
            ):
                if lentity == rentity:
                    continue
                laabb = AABB(lposition.position, Vec2(lcollider.width, lcollider.height) / 2)
                raabb = AABB(rposition.position, Vec2(rcollider.width, rcollider.height) / 2)
                md = raabb.minkowski_difference(laabb)
                if md.min.x <= 0 and md.max.x >= 0 and md.min.y <= 0 and md.max.y >= 0:
                    penetration = md.closest_point_on_bounds_to_point(Vec2(0, 0))
                    ecs.dispatch_event(ecs.COLLISION_EVENT, lentity, rentity, penetration)


class PlayerCollisionSystem(ecs.SystemProtocol):
    def process(self, *args, **kwargs):
        ...

    def on_collision(self, lentity: int, rentity: int, penetration: Vec2):
        if ecs.has_component(lentity, Player):
            position = ecs.try_component(lentity, Position)
            position.position += penetration
