import pytest
from pyglet.math import Vec2

from barfight.physics.primitives import (
    Circle,
    OrientedRectangle,
    Point,
    Polygon,
    Rectangle,
)
from barfight.physics.primitives.gjk import colliding, penetration


@pytest.mark.parametrize(
    "test_shape1,test_shape2",
    [
        (
            Rectangle(Vec2(0, 0), Vec2(1, 1)),
            Rectangle(Vec2(0.5, 0), Vec2(1, 1)),
        ),  # overlapping
        (
            Rectangle(Vec2(0, 0), Vec2(1.0001, 1)),
            Rectangle(Vec2(1, 1), Vec2(1, 1)),
        ),  # edge
        (Circle(Vec2(0, 0), 1), Circle(Vec2(0.5, 0), 1)),  # overlapping
        (Circle(Vec2(0, 0), 1), Circle(Vec2(1, 0), 1)),  # edge
        (
            OrientedRectangle(Vec2(0, 0), Vec2(5, 5), 45),
            OrientedRectangle(Vec2(0.5, 0), Vec2(5, 5), 45),
        ),
        (
            Polygon([Vec2(-1, -1), Vec2(0, 1), Vec2(1, -1)]),
            Polygon([Vec2(-1, 1), Vec2(0, -1), Vec2(1, 1)]),
        ),
    ],
)
def test_colliding_intersection(test_shape1, test_shape2):
    result = colliding(test_shape1, test_shape2)

    assert None is not result


@pytest.mark.parametrize(
    "test_shape1,test_shape2",
    [
        (Rectangle(Vec2(0, 0), Vec2(1, 1)), Rectangle(Vec2(0, 2), Vec2(1, 1))),
        (Circle(Vec2(0, 0), 1), Circle(Vec2(10, 0), 1)),
        (
            OrientedRectangle(Vec2(0, 0), Vec2(5, 5), 45),
            OrientedRectangle(Vec2(10, 10), Vec2(5, 5), 45),
        ),
        (
            Polygon([Vec2(-1, -1), Vec2(0, 1), Vec2(1, -1)]),
            Polygon([Vec2(10, 10), Vec2(10.5, 11), Vec2(11, 10)]),
        ),
        (Point(Vec2(0, 0)), Point(Vec2(1, 0))),
    ],
)
def test_colliding_no_intersection(test_shape1, test_shape2):
    result = colliding(test_shape1, test_shape2)

    assert None is result


@pytest.mark.parametrize(
    "test_shape1,test_shape2,expected",
    [
        (
            Rectangle(Vec2(0, 0), Vec2(1, 1)),
            Rectangle(Vec2(0.5, 0), Vec2(1, 1)),
            Vec2(0.5, 0),
        ),
        (Circle(Vec2(0, 0), 1), Circle(Vec2(0.5, 0), 1), Vec2(1.5, 0)),  # overlapping
        (Circle(Vec2(0, 0), 1), Circle(Vec2(1, 0), 1), Vec2(1, 0)),  # edge
        (
            OrientedRectangle(Vec2(0, 0), Vec2(5, 5), 45),
            OrientedRectangle(Vec2(0.5, 0), Vec2(5, 5), 45),
            Vec2(0.5, 0),
        ),
        (
            Polygon([Vec2(-1, -1), Vec2(0, 1), Vec2(1, -1)]),
            Polygon([Vec2(-1, 1), Vec2(0, -1), Vec2(1, 1)]),
            Vec2(0.5, 0),
        ),
    ],
)
def test_penetration(test_shape1, test_shape2, expected):
    collision = colliding(test_shape1, test_shape2)
    result = penetration(collision)

    assert pytest.approx(expected.x, rel=1e-2, abs=1e-2) == result.x
    assert pytest.approx(expected.y, rel=1e-2, abs=1e-2) == result.y
