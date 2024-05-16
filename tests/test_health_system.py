from barfight import ecs
from barfight.components import Health
from barfight.systems import HealthSystem


def test_health_kills_on_zero_health(ecs_world):
    ecs.add_system(HealthSystem())
    entity = ecs.create_entity(Health(0, 10))
    ecs.update(0.0)

    assert not ecs.entity_exists(entity)


def test_health_skips_living(ecs_world):
    ecs.add_system(HealthSystem())
    entity = ecs.create_entity(Health(10, 10))
    ecs.update(0.0)

    assert ecs.entity_exists(entity)
