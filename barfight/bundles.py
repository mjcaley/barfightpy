import pyglet
from pyglet.math import Vec2

from . import ecs
from .components import (
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
from .physics import Body, BodyKind, Rectangle

# fmt: off
CHARACTER_LAYER = 0b0001
OBSTACLE_LAYER =  0b0010
ATTACK_LAYER =    0b0100
CHARACTER_MASK =  0b0010
OBSTACLE_MASK =   0b0000
ATTACK_MASK =     0b0001
# fmt: on


def add_player():
    image = pyglet.image.load("assets/player.png")
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

    entity = ecs.create_entity(
        Player(max_speed=120),
        Position(),
        Velocity(),
        Sprite(pyglet.sprite.Sprite(image), Layer.Game),
        Health(100, 100),
    )
    ecs.add_component(
        entity,
        PhysicsBody(
            Body(
                Rectangle.from_dimensions(Vec2(0, 0), 100, 100),
                layer=CHARACTER_LAYER,
                mask=CHARACTER_MASK,
                data=entity,
            )
        ),
    )

    return entity


def add_enemy(x: float, y: float):
    image = pyglet.image.load("assets/player.png")
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

    entity = ecs.create_entity(
        Enemy(),
        Position(Vec2(x, y)),
        Velocity(speed=120),
        Sprite(pyglet.sprite.Sprite(image), Layer.Game),
        Health(100, 100),
    )
    ecs.add_component(
        entity,
        PhysicsBody(Body(Rectangle.from_dimensions(Vec2(x, y), 100, 100), data=entity)),
    )

    return entity


def add_wall(x: float, y: float, width: float, height: float):
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


def add_attack(entity: int, min: Vec2, max: Vec2):
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
