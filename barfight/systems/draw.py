import esper
from pyglet.graphics import Batch
from pyglet.window import Window

from ..components import Position, Sprite


class DrawSystem(esper.Processor):
    def process(self, *_): ...

    def on_draw(self, window: Window):
        window.clear()
        batch = Batch()
        for _, (position, sprite) in esper.get_components(Position, Sprite):
            sprite.sprite.update(x=position.position.x, y=position.position.y)
            sprite.sprite.batch = batch
        batch.draw()
