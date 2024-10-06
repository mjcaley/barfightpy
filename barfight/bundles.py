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
from .constants import (
    ATTACK_LAYER,
    ATTACK_MASK,
    CHARACTER_LAYER,
    CHARACTER_MASK,
    OBSTACLE_LAYER,
    OBSTACLE_MASK,
)
from .physics import Body, BodyKind, Rectangle


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
    ecs.add_component(
        entity,
        PhysicsBody(
            Body(
                Rectangle.from_dimensions(position, 100, 100),
                layer=CHARACTER_LAYER,
                mask=CHARACTER_MASK,
                data=entity,
            )
        ),
    )

    return entity


def add_enemy(x: float, y: float) -> int:
    image = pyglet.image.load("assets/player.png")
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

    entity = ecs.create_entity(
        Enemy(),
        Position(Vec2(x, y)),
        Velocity(),
        Sprite(pyglet.sprite.Sprite(image), Layer.Game),
        Health(100, 100),
        Actor(max_speed=200),
    )
    ecs.add_component(
        entity,
        PhysicsBody(
            Body(
                Rectangle.from_dimensions(Vec2(x, y), 100, 100),
                layer=CHARACTER_LAYER,
                mask=CHARACTER_MASK,
                data=entity,
            )
        ),
    )

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
    ecs.add_component(
        entity,
        PhysicsBody(
            Body(
                Rectangle.from_dimensions(Vec2(x, y), width, height),
                kind=BodyKind.Static,
                layer=OBSTACLE_LAYER,
                mask=OBSTACLE_MASK,
                data=entity,
            )
        ),
    )

    return entity


def add_attack(entity: int, min: Vec2, max: Vec2) -> int:
    rect = Rectangle(min, max)
    entity = ecs.create_entity(
        Attack(entity),
        Position(rect.center),
    )
    ecs.add_component(
        entity,
        PhysicsBody(
            Body(
                rect,
                kind=BodyKind.Sensor,
                layer=ATTACK_LAYER,
                mask=ATTACK_MASK,
                data=entity,
            )
        ),
    )

    return entity
