import esper
import pyglet

from .components import Player, Position, Sprite, Velocity


def add_player():
    player_img = pyglet.image.load("barfight/assets/player.png")
    player_img.anchor_x = player_img.width // 2
    player_img.anchor_y = player_img.height // 2

    entity = esper.create_entity(
        Player(),
        Position(),
        Velocity(speed=80),
        Sprite(pyglet.sprite.Sprite(player_img))
    )

    return entity
