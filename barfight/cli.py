import pyglet
from pyglet.window import Window

from . import ecs
from .bundles import add_enemy, add_player, add_wall
from .systems.collision import CollisionSystem
from .systems.debug import DebugSystem
from .systems.draw import DrawSystem
from .systems.input import InputSystem
from .systems.movement import MovementSystem
from .systems.player import PlayerSystem


def main():
    window = Window(800, 600, "Bar Fight")

    debug_system = DebugSystem()
    ecs.add_system(debug_system, 100)
    ecs.set_handler(ecs.COLLISION_EVENT, debug_system.on_collision)
    ecs.set_handler(ecs.DRAW_EVENT, debug_system.on_draw)
    ecs.set_handler(ecs.COMPONENT_ADDED_EVENT, debug_system.on_component_added)
    ecs.set_handler(ecs.COMPONENT_REMOVED_EVENT, debug_system.on_component_removed)

    input_system = InputSystem()
    ecs.add_system(input_system)

    ecs.add_system(MovementSystem())

    ecs.add_system(CollisionSystem())
    collision_system = CollisionSystem()
    ecs.add_system(collision_system)

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

    player_system = PlayerSystem()
    ecs.add_system(player_system)

    player = add_player()
    wall1 = add_wall(400, 200, 100, 100)
    wall2 = add_wall(500, 200, 100, 100)
    wall2 = add_wall(600, 200, 100, 100)
    wall2 = add_wall(700, 200, 100, 100)
    wall2 = add_wall(800, 200, 100, 100)
    enemy1 = add_enemy(400, 300)

    pyglet.app.run()
