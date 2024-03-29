import esper
import pyglet
from pyglet.math import Vec2

from .components import BoxCollider, Player, Position, Sprite, Velocity


def add_player():
    player_img = pyglet.image.load("barfight/assets/player.png")
    player_img.anchor_x = player_img.width // 2
    player_img.anchor_y = player_img.height // 2

    entity = esper.create_entity(
        Player(),
        Position(),
        Velocity(speed=80),
        Sprite(pyglet.sprite.Sprite(player_img)),
        BoxCollider(player_img.width, player_img.height)
    )

    return entity


def add_enemy(x: float, y: float):
    player_img = pyglet.image.load("barfight/assets/player.png")
    player_img.anchor_x = player_img.width // 2
    player_img.anchor_y = player_img.height // 2

    entity = esper.create_entity(
        Position(Vec2(x, y)),
        Velocity(speed=80),
        Sprite(pyglet.sprite.Sprite(player_img)),
        BoxCollider(player_img.width, player_img.height)
    )

    return entity
