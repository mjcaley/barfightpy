from functools import partial

from .. import ecs
from ..components import Player, Position, Velocity, Wall
from . import protocols
from .collision import AABB, distance, rect_rect_resolve, rect_vs_rect


class MovementSystem(ecs.SystemProtocol, protocols.CollisionProtocol):
    def process(self, dt: float):
        for entity, (_, position, velocity) in ecs.get_components(
            Player, Position, Velocity
        ):
            position.position += velocity.direction * velocity.speed * dt

    def on_collision(self, source: AABB, collisions: list[AABB]):
        if not ecs.has_component(source.entity, Player):
            return
        collisions.sort(key=partial(distance, source.position.position))
        for target in collisions:
            if not ecs.has_component(target.entity, Wall):
                continue
            if rect_vs_rect(source, target):
                resolve = rect_rect_resolve(source, target)
                source.position.position += resolve
