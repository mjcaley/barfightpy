from math import radians

import pyglet
import pyglet.info
from loguru import logger
from pyglet.math import Vec2
from pyglet.window import Window
from pyglet.window.key import KeyStateHandler
from pyglet.window.mouse import MouseStateHandler

from barfight.pathfinding import Grid, Pathfinding

from . import ecs, events
from .bundles import add_enemy, add_player, add_rotated_wall, add_sensor, add_wall
from .physics.world import PhysicsWorld
from .systems import (
    AISystem,
    ActorSystem,
    AttackSystem,
    DebugSystem,
    DrawSystem,
    HealthSystem,
    InputSystem,
    MovementSystem,
    PhysicsSystem,
)


def main():
    logger.disable("barfight")
    logger.enable("barfight.physics")

    window = Window(800, 600, "Bar Fight")
    world = PhysicsWorld(Vec2(-200, -200), Vec2(2000, 1500))

    debug_system = DebugSystem()
    ecs.add_system(debug_system, 100)
    ecs.add_handlers(debug_system)

    key_state_handler = KeyStateHandler()
    mouse_state_handler = MouseStateHandler()
    window.push_handlers(key_state_handler, mouse_state_handler)
    input_system = InputSystem(key_state_handler, mouse_state_handler)
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

    @window.event
    def on_mouse_press(x: int, y: int, button: int, modifiers: int):
        ecs.dispatch_event(events.MOUSE_DOWN_EVENT, x, y, button, modifiers)

    @window.event
    def on_mouse_release(x: int, y: int, button: int, modifiers: int):
        ecs.dispatch_event(events.MOUSE_UP_EVENT, x, y, button, modifiers)

    window.push_handlers(input_system.key_handler)
    pyglet.clock.schedule_interval(ecs.update, interval=1.0 / 60)

    player_system = ActorSystem()
    ecs.add_system(player_system)
    ecs.add_handlers(player_system)

    health_system = HealthSystem()
    ecs.add_system(health_system)

    attack_system = AttackSystem()
    ecs.add_system(attack_system)
    ecs.add_handlers(attack_system)

    add_player(Vec2(200, 200))
    add_wall(400, 200, 100, 100)
    add_wall(500, 200, 100, 100)
    add_wall(600, 200, 100, 100)
    add_wall(700, 200, 100, 100)
    add_wall(800, 200, 100, 100)
    add_rotated_wall(400, 350, radians(45))
    add_enemy(Vec2(200, 300))
    add_sensor(Vec2(200, 100), Vec2(25, 25))

    pathfinding = Pathfinding(Grid(world, 5))
    ai_system = AISystem(pathfinding, window)
    ecs.add_system(ai_system)
    ecs.add_handlers(ai_system)

    pyglet.info.dump_gl()
    pyglet.app.run()
