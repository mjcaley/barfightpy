import pyglet
from pyglet.window import Window

from . import ecs
from .bundles import add_enemy, add_player, add_wall
from .match_extensions import patch_vec2
from .systems.attack import AttackSystem
from .systems.collision import CollisionSystem
from .systems.debug import DebugSystem
from .systems.draw import DrawSystem
from .systems.health import HealthSystem
from .systems.input import InputSystem
from .systems.movement import MovementSystem
from .systems.player import PlayerSystem


def main():
    patch_vec2()

    window = Window(800, 600, "Bar Fight")

    debug_system = DebugSystem()
    ecs.add_system(debug_system, 100)
    ecs.set_handler(ecs.COLLISION_EVENT, debug_system.on_collision)
    ecs.set_handler(ecs.COMPONENT_ADDED_EVENT, debug_system.on_component_added)
    ecs.set_handler(ecs.COMPONENT_REMOVED_EVENT, debug_system.on_component_removed)

    input_system = InputSystem()
    ecs.add_system(input_system)
    ecs.set_handler(ecs.KEY_UP_EVENT, input_system.on_key_up)
    ecs.set_handler(ecs.KEY_DOWN_EVENT, input_system.on_key_down)

    movement_system = MovementSystem()
    ecs.add_system(movement_system)
    ecs.set_handler(ecs.COLLISION_EVENT, movement_system.on_collision)

    collision_system = CollisionSystem()
    ecs.add_system(collision_system)

    draw_system = DrawSystem()
    ecs.add_system(draw_system)
    ecs.set_handler(ecs.DRAW_EVENT, draw_system.on_draw)
    ecs.set_handler(ecs.COMPONENT_ADDED_EVENT, draw_system.on_component_added)

    # Wire events
    @window.event
    def on_draw():
        window.clear()
        ecs.dispatch_event(ecs.DRAW_EVENT, window)

    @window.event
    def on_key_press(key: int, modifiers: int):
        ecs.dispatch_event(ecs.KEY_DOWN_EVENT, key, modifiers)

    @window.event
    def on_key_release(key: int, modifiers: int):
        ecs.dispatch_event(ecs.KEY_UP_EVENT, key, modifiers)

    window.push_handlers(input_system.handler)
    pyglet.clock.schedule_interval(ecs.update, interval=1.0 / 60)

    player_system = PlayerSystem()
    ecs.add_system(player_system)
    ecs.set_handler(ecs.PLAYER_ATTACK_EVENT, player_system.on_player_attack)
    ecs.set_handler(ecs.PLAYER_DIRECTION_EVENT, player_system.on_player_direction)

    health_system = HealthSystem()
    ecs.add_system(health_system)

    attack_system = AttackSystem()
    ecs.add_system(attack_system)
    ecs.set_handler(ecs.COLLISION_EVENT, attack_system.on_collision)

    player = add_player()
    wall1 = add_wall(400, 200, 100, 100)
    wall2 = add_wall(500, 200, 100, 100)
    wall2 = add_wall(600, 200, 100, 100)
    wall2 = add_wall(700, 200, 100, 100)
    wall2 = add_wall(800, 200, 100, 100)
    enemy1 = add_enemy(400, 300)

    pyglet.app.run()
