from loguru import logger
import pyglet
from pyglet.math import Vec2

from .. import ecs
from ..components import BoxCollider, Position, Velocity


class DebugSystem(ecs.SystemProtocol):
    def process(self, *args): ...

    def on_collision(self, lentity: int, rentity: int, penetration: Vec2):
        lposition, lcollider = ecs.try_components(lentity, Position, BoxCollider)
        lvelocity = ecs.try_component(lentity, Velocity)
        rposition, rcollider = ecs.try_components(rentity, Position, BoxCollider)
        rvelocity = ecs.try_component(rentity, Velocity)
        logger.debug(
            "Collision detected - {lentity} [Position {lposition}] [Velocity {lvelocity}] [Collider {lcollider}] : {rentity} [Position {rposition}] [Velocity {rvelocity}] [Collider {rcollider}] - [Penetration Vector {penetration}]",
            lentity=lentity, lposition=lposition, lvelocity=lvelocity, lcollider=lcollider,
            rentity=rentity, rposition=rposition, rvelocity=rvelocity, rcollider=rcollider,
            penetration=penetration)

    def on_draw(self, window: pyglet.window.Window):
        batch = pyglet.graphics.Batch()
        shapes = []
        for entity, (position, collider) in ecs.get_components(Position, BoxCollider):
            shape = pyglet.shapes.Box(position.position.x, position.position.y, collider.width, collider.height, color=(50, 25, 255), batch=batch)
            shape.anchor_position = (collider.width / 2, collider.height / 2)
            shapes.append(shape)
        batch.draw()
        for shape in shapes:
            shape.delete()
