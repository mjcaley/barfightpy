import esper
import pyglet
from pyglet.window import Window

from .bundles import add_player
from .systems.draw import DrawSystem
from .systems.input import InputSystem
from .systems.movement import MovementSystem


def main():
    window = Window(800, 600, "Bar Fight")

    input_system = InputSystem()
    esper.add_processor(input_system)

    esper.add_processor(MovementSystem())

    draw_system = DrawSystem()
    esper.add_processor(draw_system)
    esper.set_handler("draw", draw_system.on_draw)

    player = add_player()

    # Wire events
    @window.event
    def on_draw():
        esper.dispatch_event("draw", window)
    
    window.push_handlers(input_system.handler)
    pyglet.clock.schedule_interval(esper.process, interval=1.0 / 60)

    pyglet.app.run()
