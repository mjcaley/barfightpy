from typing import Any

import pyglet
from loguru import logger

from .. import ecs
from ..components import BoxCollider, Layer, Position, Shape, Velocity
from . import protocols
from .collision import AABB


class DebugSystem(
    ecs.SystemProtocol,
    protocols.ComponentAddedProtocol,
    protocols.ComponentRemovedProtocol,
    protocols.CollisionProtocol,
):
    def process(self, *args): ...

    def on_collision(self, source: AABB, collisions: list[AABB]):
        lposition, lcollider = ecs.try_components(source.entity, Position, BoxCollider)
        lvelocity = ecs.try_component(source.entity, Velocity)

        for collision in collisions:
            rposition, rcollider = ecs.try_components(
                collision.entity, Position, BoxCollider
            )
            rvelocity = ecs.try_component(collision.entity, Velocity)
            logger.debug(
                "Collision detected - {lentity} [Position {lposition}] [Velocity {lvelocity}] [Collider {lcollider}] : {rentity} [Position {rposition}] [Velocity {rvelocity}] [Collider {rcollider}]",
                lentity=source.entity,
                lposition=lposition,
                lvelocity=lvelocity,
                lcollider=lcollider,
                rentity=collision.entity,
                rposition=rposition,
                rvelocity=rvelocity,
                rcollider=rcollider,
            )

    def on_component_added(self, entity: int, component: Any):
        if isinstance(component, BoxCollider):
            shape = pyglet.shapes.Box(
                0, 0, component.width, component.height, color=(50, 25, 255)
            )
            shape.anchor_position = (component.width / 2, component.height / 2)
            ecs.add_component(entity, Shape(shape, Layer.Debug))

    def on_component_removed(self, entity: int, component: Any):
        if isinstance(component, BoxCollider):
            ecs.remove_component(entity, Shape)
