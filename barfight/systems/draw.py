from pyglet.graphics import Batch, Group
from pyglet.window import Window

from .. import ecs
from ..components import Layer, Position, Shape, Sprite
from . import protocols


class DrawSystem(
    ecs.SystemProtocol, protocols.DrawProtocol, protocols.ComponentAddedProtocol
):
    def __init__(self):
        self.game_layer = Group(Layer.Game)
        self.debug_layer = Group(Layer.Debug)
        self.batch = Batch()

    def process(self, *_): ...

    def on_draw(self, window: Window):
        for _, (position, sprite) in ecs.get_components(Position, Sprite):
            sprite.sprite.update(x=position.position.x, y=position.position.y)
        for _, (position, shape) in ecs.get_components(Position, Shape):
            shape.shape.x = position.position.x
            shape.shape.y = position.position.y
        self.batch.draw()

    def on_component_added(self, entity: int, component: ecs.Any):
        if isinstance(component, Sprite):
            component.sprite.batch = self.batch
            match component.layer:
                case Layer.Game:
                    component.sprite.group = self.game_layer
                case Layer.Debug:
                    component.sprite.group = self.debug_layer
        elif isinstance(component, Shape):
            component.shape.batch = self.batch
            match component.layer:
                case Layer.Game:
                    component.shape.group = self.game_layer
                case Layer.Debug:
                    component.shape.group = self.debug_layer
