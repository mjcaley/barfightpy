import pytest
from pyglet.math import Vec2

from barfight import ecs, events
from barfight.components import PhysicsBody, Player, PlayerState, Position, Velocity
from barfight.physics import Body, Rectangle
from barfight.systems import PlayerSystem


@pytest.fixture
def player_entity(ecs_world):
    player = Player(max_speed=10)
    position = Position()
    velocity = Velocity()
    physics_body = PhysicsBody(Body(Rectangle(Vec2(), Vec2())))
    ecs.create_entity(player, position, velocity, physics_body)

    yield player, position, velocity


def test_player_idle_to_idle(player_entity):
    ecs.add_system(PlayerSystem())
    player, position, velocity = player_entity
    ecs.update(1 / 60)

    assert PlayerState.Idle == player.state


def test_player_idle_to_walking(player_entity):
    ecs.add_system(PlayerSystem())
    player, position, velocity = player_entity
    player.direction = Vec2(1, 0)
    ecs.update(1 / 60)

    assert PlayerState.Walking == player.state
    assert 1 == player.facing
    assert velocity.direction == player.direction
    assert velocity.speed == player.max_speed


def test_player_walking_to_idle(player_entity):
    ecs.add_system(PlayerSystem())
    player, position, velocity = player_entity
    player.state = PlayerState.Walking
    player.direction = Vec2(0, 0)
    ecs.update(1 / 60)

    assert PlayerState.Idle == player.state
    assert Vec2() == velocity.direction
    assert 0 == velocity.speed


def test_player_walking_to_walking(player_entity):
    ecs.add_system(PlayerSystem())
    player, position, velocity = player_entity
    player.state = PlayerState.Walking
    player.direction = Vec2(1, 0)
    ecs.update(1 / 60)

    assert PlayerState.Walking == player.state
    assert 1 == player.facing
    assert player.direction == velocity.direction


def test_player_attacking_cooldown(player_entity):
    ecs.add_system(PlayerSystem())
    player, position, velocity = player_entity
    player.state = PlayerState.Attacking
    player.cooldown = 1
    ecs.update(1 / 60)

    assert PlayerState.Attacking == player.state
    assert 1 - 1 / 60 == player.cooldown


def test_player_attacking_to_idle(player_entity):
    ecs.add_system(PlayerSystem())
    player, position, velocity = player_entity
    player.state = PlayerState.Attacking
    ecs.update(1 / 60)

    assert PlayerState.Idle == player.state
    assert Vec2() == velocity.direction
    assert 0 == velocity.speed


def test_player_attacking_to_walking(player_entity):
    ecs.add_system(PlayerSystem())
    player, position, velocity = player_entity
    player.state = PlayerState.Attacking
    player.direction = Vec2(1, 0)
    ecs.update(1 / 60)

    assert PlayerState.Walking == player.state
    assert player.direction == velocity.direction
    assert player.max_speed == velocity.speed


@pytest.mark.parametrize("state", [PlayerState.Idle, PlayerState.Walking])
def test_player_other_to_attacking(player_entity, state):
    player_system = PlayerSystem()
    ecs.add_system(player_system)
    ecs.set_handler(events.PLAYER_ATTACK_EVENT, player_system.on_player_attack)
    player, position, velocity = player_entity
    player.state = state
    player.direction = Vec2(1, 0)
    ecs.dispatch_event(events.PLAYER_ATTACK_EVENT)

    assert PlayerState.Attacking == player.state
    assert 0.2 == player.cooldown
    assert Vec2() == velocity.direction
    assert 0 == velocity.speed


def test_player_attacking_to_attacking(player_entity):
    player_system = PlayerSystem()
    ecs.add_system(player_system)
    ecs.set_handler(events.PLAYER_ATTACK_EVENT, player_system.on_player_attack)
    player, position, velocity = player_entity
    player.state = PlayerState.Attacking
    player.cooldown = 0
    ecs.dispatch_event(events.PLAYER_ATTACK_EVENT)

    assert PlayerState.Attacking == player.state
    assert 0.2 == player.cooldown
