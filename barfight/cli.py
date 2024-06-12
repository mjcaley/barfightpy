import pyglet
from pyglet.math import Vec2
from pyglet.window import Window
from pyglet.window.key import KeyStateHandler

from . import ecs, events
from .bundles import add_enemy, add_player, add_wall
from .physics import PhysicsWorld
from .systems import (
    AttackSystem,
    DebugSystem,
    DrawSystem,
    HealthSystem,
    InputSystem,
    MovementSystem,
    PhysicsSystem,
    PlayerSystem,
)


def main():
    window = Window(800, 600, "Bar Fight")
    world = PhysicsWorld(Vec2(-200, -200), Vec2(1000, 800))

    debug_system = DebugSystem()
    ecs.add_system(debug_system, 100)
    ecs.add_handlers(debug_system)

    key_state_handler = KeyStateHandler()
    window.push_handlers(key_state_handler)
    input_system = InputSystem(key_state_handler)
    ecs.add_system(input_system)
    ecs.add_handlers(input_system)

    movement_system = MovementSystem()
    ecs.add_system(movement_system)
    ecs.add_handlers(movement_system)

    physics_system = PhysicsSystem(world)
    ecs.add_system(physics_system)
    ecs.add_handlers(physics_system)

    draw_system = DrawSystem()
    ecs.add_system(draw_system)
    ecs.add_handlers(draw_system)

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
    ecs.add_handlers(player_system)

    health_system = HealthSystem()
    ecs.add_system(health_system)

    attack_system = AttackSystem()
    ecs.add_system(attack_system)
    ecs.add_handlers(attack_system)

    player = add_player()
    wall1 = add_wall(400, 200, 100, 100)
    wall2 = add_wall(500, 200, 100, 100)
    wall2 = add_wall(600, 200, 100, 100)
    wall2 = add_wall(700, 200, 100, 100)
    wall2 = add_wall(800, 200, 100, 100)
    enemy1 = add_enemy(400, 300)

    pyglet.app.run()
