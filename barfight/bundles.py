from math import inf

import pyglet
from pyglet.math import Vec2
from pymunk import Body, Poly

from . import ecs
from .components import (
    Actor,
    Attack,
    Enemy,
    Health,
    Layer,
    PhysicsBody,
    Player,
    Position,
    Sprite,
    Velocity,
    Wall,
)

# from .physics.body import Body, BodyKind
# from .physics.shapes import OrientedRectangleShape, RectangleShape

COLLISION_ACTOR = 1
COLLISION_WALL = 2


def add_player(position: Vec2) -> int:
    image = pyglet.image.load("assets/player.png")
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

    entity = ecs.create_entity(
        Actor(max_speed=120),
        Position(position),
        Velocity(),
        Sprite(pyglet.sprite.Sprite(image), Layer.Game),
        Health(100, 100),
        Player(),
    )
    body = Body(1, moment=inf)
    body.data = entity
    shape = Poly(
        body,
        [
            (position.x - 50, position.y - 50),
            (position.x - 50, position.y + 50),
            (position.x + 50, position.y + 50),
            (position.x + 50, position.y - 50),
        ],
    )
    shape.collision_type = COLLISION_ACTOR
    shape.elasticity = 0
    ecs.add_component(entity, PhysicsBody(body, [shape]))

    return entity


def add_enemy(position: Vec2) -> int:
    image = pyglet.image.load("assets/player.png")
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

    entity = ecs.create_entity(
        Enemy(),
        Position(position),
        Velocity(),
        Sprite(pyglet.sprite.Sprite(image), Layer.Game),
        Health(100, 100),
        Actor(max_speed=200),
    )
    body = Body(1, moment=inf)
    body.data = entity
    shape = Poly(
        body,
        [
            (position.x - 50, position.y - 50),
            (position.x - 50, position.y + 50),
            (position.x + 50, position.y + 50),
            (position.x + 50, position.y - 50),
        ],
    )
    shape.collision_type = COLLISION_ACTOR
    ecs.add_component(entity, PhysicsBody(body, [shape]))

    return entity


def add_wall(x: float, y: float, width: float, height: float) -> int:
    image = pyglet.image.load("assets/wall.png")
    image.anchor_x = image.width // 2
    image.anchor_y = image.width // 2

    entity = ecs.create_entity(
        Wall(),
        Position(Vec2(x, y)),
        Sprite(pyglet.sprite.Sprite(image), Layer.Game),
    )
    body = Body(body_type=Body.STATIC)
    body.data = entity
    shape = Poly(
        body, [(x, y), (x, y + height), (x + width, y + height), (x + width, y)]
    )
    shape.collision_type = COLLISION_WALL
    shape.elasticity = 0
    ecs.add_component(entity, PhysicsBody(body, [shape]))

    return entity


def add_rotated_wall(x: float, y: float, rotation: float) -> int:
    ...
    # entity = ecs.create_entity(
    #     Wall(),
    #     Position(Vec2(x, y)),
    # )
    # ecs.add_component(
    #     entity,
    #     PhysicsBody(
    #         Body(
    #             OrientedRectangleShape(
    #                 Vec2(x, y),
    #                 Vec2(25, 25),
    #                 rotation,
    #             ),
    #             BodyKind.Static,
    #             data=entity,
    #         )
    #     )
    # )

    # return entity


def add_attack(attack_entity: int, origin: Vec2, size: Vec2) -> int:
    entity = ecs.create_entity(
        Attack(attack_entity),
        Position(origin + (size / 2)),
    )
    body = Body(body_type=Body.STATIC)
    body.data = entity
    shape = Poly(
        body,
        [
            (origin.x, origin.y),
            (origin.x, origin.y + size.y),
            (origin.x + size.x, origin.y + size.y),
            (origin.x + size.x, origin.y),
        ],
    )
    ecs.add_component(entity, PhysicsBody(body, [shape]))

    return entity


def add_sensor(origin: Vec2, size: Vec2) -> int:
    entity = ecs.create_entity(Position(origin + (size / 2)))
    body = Body(body_type=Body.STATIC)
    body.data = entity
    shape = Poly(
        body,
        [
            (origin.x, origin.y),
            (origin.x, origin.y + size.y),
            (origin.x + size.x, origin.y + size.y),
            (origin.x + size.x, origin.y),
        ],
    )
    shape.sensor = True
    ecs.add_component(entity, PhysicsBody(body, [shape]))

    return entity
