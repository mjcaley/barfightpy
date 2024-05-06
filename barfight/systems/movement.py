from .. import ecs
from ..components import Player, Position, Velocity


class MovementSystem(ecs.SystemProtocol):
    def process(self, dt: float):
        for entity, (_, position, velocity) in ecs.get_components(
            Player, Position, Velocity
        ):
            position.position += velocity.direction * velocity.speed * dt
