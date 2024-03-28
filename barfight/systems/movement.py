import esper

from ..components import Position, Velocity


class MovementSystem(esper.Processor):
    def process(self, dt: float):
        for entity, (position, velocity) in esper.get_components(Position, Velocity):
            position.position += velocity.direction * velocity.speed * dt
            print(f"[Movement] entity: {entity} position: {position.position}")
