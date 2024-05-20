from pyglet.math import Vec2

from barfight import ecs, events
from barfight.components import BoxCollider, Player, Position, Velocity, Wall
from barfight.systems import MovementSystem


def test_movement_moves_player(ecs_world):
    direction = Vec2(1, 1).normalize()
    speed = 10
    dt = 1 / 60

    position = Position()
    ecs.create_entity(position, Velocity(direction=direction, speed=speed), Player(10))
    ecs.add_system(MovementSystem())

    ecs.update(dt)

    assert direction * speed * dt == position.position


def test_movement_collides(ecs_world):
    movement_system = MovementSystem()
    ecs.add_system(movement_system)
    ecs.set_handler(events.COLLISION_EVENT, movement_system.on_collision)

    player_pos = Position(Vec2(0, 0))
    player = ecs.create_entity(Player(10), player_pos, BoxCollider(10, 10))
    wall = ecs.create_entity(Wall(), Position(Vec2(5, 0)), BoxCollider(10, 10))

    ecs.dispatch_event(events.COLLISION_EVENT, player, {wall})

    assert Vec2(-5, 0) == player_pos.position


def test_movement_collision_not_a_player(ecs_world):
    movement_system = MovementSystem()
    ecs.add_system(movement_system)
    ecs.set_handler(events.COLLISION_EVENT, movement_system.on_collision)

    obj_pos = Position(Vec2(0, 0))
    obj = ecs.create_entity(obj_pos, BoxCollider(10, 10))
    wall = ecs.create_entity(Wall(), Position(Vec2(5, 0)), BoxCollider(10, 10))

    ecs.dispatch_event(events.COLLISION_EVENT, obj, {wall})

    assert Vec2() == obj_pos.position


def test_movement_collision_not_a_wall(ecs_world):
    movement_system = MovementSystem()
    ecs.add_system(movement_system)
    ecs.set_handler(events.COLLISION_EVENT, movement_system.on_collision)

    player_pos = Position(Vec2(0, 0))
    player = ecs.create_entity(Player(10), player_pos, BoxCollider(10, 10))
    obj = ecs.create_entity(Position(Vec2(5, 0)), BoxCollider(10, 10))

    ecs.dispatch_event(events.COLLISION_EVENT, player, {obj})

    assert Vec2() == player_pos.position
