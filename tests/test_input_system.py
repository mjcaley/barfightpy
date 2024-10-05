import pytest
from pyglet.math import Vec2
from pyglet.window import key
from pyglet.window.key import KeyStateHandler

from barfight import ecs, events
from barfight.components import Actor
from barfight.systems import InputSystem


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (key.W, Vec2(0, 1)),
        (key.S, Vec2(0, -1)),
        (key.A, Vec2(-1, 0)),
        (key.D, Vec2(1, 0)),
    ],
)
def test_input_sets_direction(ecs_world, test_input, expected):
    handler = KeyStateHandler()
    ecs.add_system(InputSystem(handler))

    player = Actor(0)
    ecs.create_entity(player)

    handler.on_key_press(test_input, 0)
    ecs.update(0.0)

    assert expected == player.direction


def test_input_on_key_down(ecs_world):
    attacked = False

    def on_player_attack():
        nonlocal attacked
        attacked = True

    ecs.set_handler(events.PLAYER_ATTACK_EVENT, on_player_attack)

    input_system = InputSystem(KeyStateHandler())
    ecs.add_system(input_system)

    input_system.on_key_down(key.N, 0)

    assert attacked
