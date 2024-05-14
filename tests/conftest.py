import pytest

from barfight import ecs


@pytest.fixture
def ecs_world():
    ecs.switch_world("pytest")
    yield
    ecs.switch_world("default")
    ecs.delete_world("pytest")
