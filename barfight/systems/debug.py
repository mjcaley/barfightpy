from typing import Any

import pyglet
from loguru import logger

from .. import ecs
from ..components import BoxCollider, Layer, Position, Shape, Velocity


class DebugSystem(
    ecs.SystemProtocol,
    ecs.ComponentAddedProtocol,
    ecs.ComponentRemovedProtocol,
    ecs.CollisionProtcol,
):
    def process(self, *args): ...

    def on_collision(self, source: int, target: int):
        lposition, lcollider = ecs.try_components(source, Position, BoxCollider)
        lvelocity = ecs.try_component(source, Velocity)
        rposition, rcollider = ecs.try_components(target, Position, BoxCollider)
        rvelocity = ecs.try_component(target, Velocity)
        logger.debug(
            "Collision detected - {lentity} [Position {lposition}] [Velocity {lvelocity}] [Collider {lcollider}] : {rentity} [Position {rposition}] [Velocity {rvelocity}] [Collider {rcollider}]",
            lentity=source,
            lposition=lposition,
            lvelocity=lvelocity,
            lcollider=lcollider,
            rentity=target,
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
