import pyglet
from pyglet.window import Window
from pyglet.window.key import KeyStateHandler

from . import ecs, events
from .bundles import add_enemy, add_player, add_wall
from .systems import (
    AttackSystem,
    CollisionSystem,
    DebugSystem,
    DrawSystem,
    HealthSystem,
    InputSystem,
    MovementSystem,
    PlayerSystem,
)


def main():
    window = Window(800, 600, "Bar Fight")

    debug_system = DebugSystem()
    ecs.add_system(debug_system, 100)
    ecs.set_handler(events.COLLISION_EVENT, debug_system.on_collision)
    ecs.set_handler(events.COMPONENT_ADDED_EVENT, debug_system.on_component_added)
    ecs.set_handler(events.COMPONENT_REMOVED_EVENT, debug_system.on_component_removed)

    key_state_handler = KeyStateHandler()
    window.push_handlers(key_state_handler)
    input_system = InputSystem(key_state_handler)
    ecs.add_system(input_system)
    ecs.set_handler(events.KEY_UP_EVENT, input_system.on_key_up)
    ecs.set_handler(events.KEY_DOWN_EVENT, input_system.on_key_down)

    movement_system = MovementSystem()
    ecs.add_system(movement_system)
    ecs.set_handler(events.COLLISION_EVENT, movement_system.on_collision)

    collision_system = CollisionSystem()
    ecs.add_system(collision_system)

    draw_system = DrawSystem()
    ecs.add_system(draw_system)
    ecs.set_handler(events.DRAW_EVENT, draw_system.on_draw)
    ecs.set_handler(events.COMPONENT_ADDED_EVENT, draw_system.on_component_added)

    # Wire events
    @window.event
    def on_draw():
        window.clear()
        ecs.dispatch_event(events.DRAW_EVENT, window)

    @window.event
    def on_key_press(key: int, modifiers: int):
        ecs.dispatch_event(events.KEY_DOWN_EVENT, key, modifiers)

    @window.event
    def on_key_release(key: int, modifiers: int):
        ecs.dispatch_event(events.KEY_UP_EVENT, key, modifiers)

    window.push_handlers(input_system.handler)
    pyglet.clock.schedule_interval(ecs.update, interval=1.0 / 60)

    player_system = PlayerSystem()
    ecs.add_system(player_system)
    ecs.set_handler(events.PLAYER_ATTACK_EVENT, player_system.on_player_attack)
    ecs.set_handler(events.PLAYER_DIRECTION_EVENT, player_system.on_player_direction)

    health_system = HealthSystem()
    ecs.add_system(health_system)

    attack_system = AttackSystem()
    ecs.add_system(attack_system)
    ecs.set_handler(events.COLLISION_EVENT, attack_system.on_collision)

    player = add_player()
    wall1 = add_wall(400, 200, 100, 100)
    wall2 = add_wall(500, 200, 100, 100)
    wall2 = add_wall(600, 200, 100, 100)
    wall2 = add_wall(700, 200, 100, 100)
    wall2 = add_wall(800, 200, 100, 100)
    enemy1 = add_enemy(400, 300)

    pyglet.app.run()
