import pyglet
from pyglet.math import Vec2

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
from .physics.body import Body, BodyKind
from .physics.shapes import RectangleShape


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
    shape = RectangleShape(position - Vec2(100, 100) / 2, Vec2(100, 100))
    # breakpoint()
    ecs.add_component(entity, PhysicsBody(Body(shape, data=entity)))

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
    shape = RectangleShape(position - Vec2(100, 100) / 2, Vec2(100, 100))
    ecs.add_component(entity, PhysicsBody(Body(shape, data=entity)))

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
    # breakpoint()
    ecs.add_component(
        entity,
        PhysicsBody(
            Body(
                RectangleShape(
                    Vec2(x, y) - Vec2(width, height) / 2, Vec2(width, height)
                ),
                kind=BodyKind.Static,
                data=entity,
            )
        ),
    )

    return entity


def add_attack(entity: int, origin: Vec2, size: Vec2) -> int:
    rect = RectangleShape(origin, size)
    entity = ecs.create_entity(
        Attack(entity),
        Position(rect.position),
    )
    ecs.add_component(
        entity,
        PhysicsBody(
            Body(
                rect,
                kind=BodyKind.Sensor,
                data=entity,
            )
        ),
    )

    return entity
