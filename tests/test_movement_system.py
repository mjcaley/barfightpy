from pyglet.math import Vec2

from barfight import ecs
from barfight.components import Actor, Position, Velocity
from barfight.systems import MovementSystem


def test_movement_moves_player(ecs_world):
    direction = Vec2(1, 1).normalize()
    speed = 10
    dt = 1 / 60

    position = Position()
    ecs.create_entity(position, Velocity(direction=direction, speed=speed), Actor(10))
    ecs.add_system(MovementSystem())

    ecs.update(dt)

    assert direction * speed * dt == position.position
