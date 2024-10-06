import pytest
from pyglet.math import Vec2

from barfight.pathfinding import Grid, Pathfinding
from barfight.physics import Body, BodyKind, PhysicsWorld, Rectangle


@pytest.fixture
def physics_world():
    p = PhysicsWorld(Vec2(), Vec2(3, 3))
    p.insert(Body(Rectangle(Vec2(1, 0), Vec2(2, 2)), BodyKind.Static))
    yield p


def test_grid_size(physics_world):
    g = Grid(physics_world, 0.5)

    assert 3 == len(g.grid)
    assert 3 == len(g.grid[0])
    assert g.grid[1][0].colliding is True
    assert g.grid[0][0].colliding is False


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (Vec2(0, 0), (0, 0)),
        (Vec2(3, 3), (3, 3)),
    ],
)
def test_coord_from_position(physics_world, test_input, expected):
    g = Grid(physics_world, 0.5)
    result = g.coord_from_position(test_input)

    assert expected == result


def test_pathfinding(physics_world):
    g = Grid(physics_world, 0.5)
    p = Pathfinding(g)
    path = p.find_path(Vec2(0, 0), Vec2(2.9, 0))

    assert Vec2(0.5, 0.5) == path[0].rectangle.center
    assert Vec2(0.5, 1.5) == path[1].rectangle.center
    assert Vec2(1.5, 2.5) == path[2].rectangle.center
    assert Vec2(2.5, 1.5) == path[3].rectangle.center
    assert Vec2(2.5, 0.5) == path[4].rectangle.center
