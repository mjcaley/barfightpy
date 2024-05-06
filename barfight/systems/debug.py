from typing import Any
import pyglet
from loguru import logger

from barfight.systems.collision import Hit

from .. import ecs
from ..components import BoxCollider, DebugCollider, Position, Velocity


class DebugSystem(
    ecs.SystemProtocol,
    ecs.ComponentAddedProtocol,
    ecs.ComponentRemovedProtocol,
    ecs.CollisionProtcol,
    ecs.DrawProtocol,
):
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.group = pyglet.graphics.Group(order=100)

    def process(self, *args): ...

    def on_collision(self, hit: Hit):
        lposition, lcollider = ecs.try_components(hit.source, Position, BoxCollider)
        lvelocity = ecs.try_component(hit.source, Velocity)
        rposition, rcollider = ecs.try_components(hit.target, Position, BoxCollider)
        rvelocity = ecs.try_component(hit.target, Velocity)
        logger.debug(
            "Collision detected - {lentity} [Position {lposition}] [Velocity {lvelocity}] [Collider {lcollider}] : {rentity} [Position {rposition}] [Velocity {rvelocity}] [Collider {rcollider}]",
            lentity=hit.source,
            lposition=lposition,
            lvelocity=lvelocity,
            lcollider=lcollider,
            rentity=hit.target,
            rposition=rposition,
            rvelocity=rvelocity,
            rcollider=rcollider,
        )

    def on_component_added(self, entity: int, component: Any):
        if isinstance(component, BoxCollider):
            shape = pyglet.shapes.Box(
                0,
                0,
                component.width,
                component.height,
                color=(50, 25, 255),
                batch=self.batch,
                group=self.group,
            )
            shape.anchor_position = (component.width / 2, component.height / 2)
            ecs.add_component(entity, DebugCollider(shape))

    def on_component_removed(self, entity: int, component: Any):
        if type(component, BoxCollider):
            ecs.remove_component(entity, DebugCollider)

    def on_draw(self, window: pyglet.window.Window):
        for _, (position, debug_collider) in ecs.get_components(
            Position, DebugCollider
        ):
            debug_collider.shape.x = position.position.x
            debug_collider.shape.y = position.position.y
        self.batch.draw()
