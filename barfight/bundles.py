import pyglet
from pyglet.math import Vec2

from . import ecs
from .components import (Attack, BoxCollider, Enemy, Health, Layer, Player,
                         Position, Sprite, Velocity, Wall)


def add_player():
    image = pyglet.image.load("assets/player.png")
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

    entity = ecs.create_entity(
        Player(),
        Position(),
        Velocity(speed=120),
        Sprite(pyglet.sprite.Sprite(image), Layer.Game),
        BoxCollider(100, 100),
        Health(100, 100),
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
        BoxCollider(100, 100),
        Health(100, 100),
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
        BoxCollider(100, 100),
    )

    return entity


def add_attack(x: float, y: float, entity: int):
    ecs.create_entity(
        Attack(entity),
        Position(Vec2(x, y)),
        BoxCollider(20, 20),
    )
