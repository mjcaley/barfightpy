from random import randint

from barfight import ecs, events
from barfight.components import Attack, Health
from barfight.physics import Arbiter
from barfight.systems import AttackSystem


def test_attack_process(ecs_world):
    a = AttackSystem()
    ecs.add_system(a)
    entity = ecs.create_entity()
    component = Attack(entity)
    ecs.add_component(entity, component)

    ecs.update(0.0)
    assert ecs.get_component(entity, Attack).cleanup is True
    ecs.update(0.0)
    assert not ecs.entity_exists(entity)


def test_attack_collision_without_attack_component(ecs_world):
    a = AttackSystem()
    ecs.add_system(a)
    ecs.set_handler(events.COLLISION_EVENT, a.on_collision)

    player_entity = randint(100, 1000)
    non_attack_entity = ecs.create_entity()

    health = Health(10, 10)
    target_entity = ecs.create_entity(health)

    ecs.dispatch_event(events.COLLISION_EVENT, non_attack_entity, {target_entity})

    assert 10 == health.current


def test_attack_collision_decrements_health(ecs_world):
    a = AttackSystem()
    ecs.add_system(a)
    ecs.set_handler(events.COLLISION_EVENT, a.on_collision)

    player_entity = randint(100, 1000)
    attack_entity = ecs.create_entity()
    ecs.add_component(attack_entity, Attack(player_entity))

    health = Health(10, 10)
    target_entity = ecs.create_entity(health)

    ecs.dispatch_event(events.COLLISION_EVENT, attack_entity, {target_entity})

    assert 0 == health.current


def test_attack_collision_ignores_attacker(ecs_world):
    a = AttackSystem()
    ecs.add_system(a)
    ecs.set_handler(events.COLLISION_EVENT, a.on_collision)

    health = Health(10, 10)
    player_entity = ecs.create_entity(health)

    attack_entity = ecs.create_entity()
    ecs.add_component(attack_entity, Attack(player_entity))

    ecs.dispatch_event(events.COLLISION_EVENT, attack_entity, {player_entity})

    assert 10 == health.current
