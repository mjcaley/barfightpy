import esper
import pyglet
from pyglet.window import Window

from barfight.systems.collision import CollisionSystem

from .systems.debug import DebugSystem

from .bundles import add_enemy, add_player
from .systems.draw import DrawSystem
from .systems.input import InputSystem
from .systems.movement import MovementSystem


def main():
    window = Window(800, 600, "Bar Fight")

    debug_system = DebugSystem()
    esper.add_processor(debug_system)
    esper.set_handler("collision", debug_system.on_collision)

    input_system = InputSystem()
    esper.add_processor(input_system)

    esper.add_processor(MovementSystem())

    esper.add_processor(CollisionSystem())

    draw_system = DrawSystem()
    esper.add_processor(draw_system)
    esper.set_handler("draw", draw_system.on_draw)

    player = add_player()
    enemy = add_enemy(400, 200)

    # Wire events
    @window.event
    def on_draw():
        esper.dispatch_event("draw", window)
    
    window.push_handlers(input_system.handler)
    pyglet.clock.schedule_interval(esper.process, interval=1.0 / 60)

    pyglet.app.run()
