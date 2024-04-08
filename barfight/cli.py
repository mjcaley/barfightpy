import pyglet
from pyglet.window import Window

from .systems.collision import CollisionSystem, PlayerCollisionSystem

from . import ecs
from .bundles import add_enemy, add_player, add_wall
from .systems.debug import DebugSystem
from .systems.draw import DrawSystem
from .systems.input import InputSystem
from .systems.movement import MovementSystem


def main():
    window = Window(800, 600, "Bar Fight")

    input_system = InputSystem()
    ecs.add_system(input_system)

    ecs.add_system(MovementSystem())

    ecs.add_system(CollisionSystem())
    player_collision_system = PlayerCollisionSystem()
    ecs.add_system(player_collision_system)
    ecs.set_handler(ecs.COLLISION_EVENT, player_collision_system.on_collision)

    draw_system = DrawSystem()
    ecs.add_system(draw_system)
    ecs.set_handler(ecs.DRAW_EVENT, draw_system.on_draw)

    # Wire events
    @window.event
    def on_draw():
        window.clear()
        ecs.dispatch_event(ecs.DRAW_EVENT, window)

    window.push_handlers(input_system.handler)
    pyglet.clock.schedule_interval(ecs.update, interval=1.0 / 60)

    player = add_player()
    wall = add_wall(400, 200, 128, 128)

    debug_system = DebugSystem()
    ecs.add_system(debug_system)
    ecs.set_handler(ecs.COLLISION_EVENT, debug_system.on_collision)
    ecs.set_handler(ecs.DRAW_EVENT, debug_system.on_draw)

    pyglet.app.run()
