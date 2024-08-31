import pytest
from barfight.pathfinding import Cell, Grid
from barfight.physics import BodyKind, PhysicsWorld, Body, Rectangle

from pyglet.math import Vec2


@pytest.fixture
def physics_world():
    p = PhysicsWorld(Vec2(), Vec2(200, 100))
    p.insert(Body(Rectangle(Vec2(), Vec2(20, 20)), BodyKind.Static))
    p.insert(Body(Rectangle(Vec2(50, 50), Vec2(60, 60)), BodyKind.Static))
    yield p


def test_grid_size(physics_world):
    g = Grid(physics_world, 5)

    assert 20 == len(g.grid)
    assert 10 == len(g.grid[0])
    assert g.grid[0][0].walkable is False
    assert g.grid[0][9].walkable is True
