from pyglet.graphics import Batch, Group
from pyglet.shapes import Box
from pyglet.window import Window

from barfight import ecs

from ..components import BoxCollider, Position, Sprite


class DrawSystem(ecs.SystemProtocol, ecs.DrawProtocol):
    def __init__(self):
        self.batch = Batch()
        self.group = Group(order=0)

    def process(self, *_): ...

    def on_draw(self, window: Window):
        batch = Batch()
        for _, (position, sprite) in ecs.get_components(Position, Sprite):
            sprite.sprite.update(x=position.position.x, y=position.position.y)
            sprite.sprite.batch = self.batch
        self.batch.draw()
