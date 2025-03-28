from math import radians

import pytest
from pyglet.math import Vec2

from barfight.physics.primitives import (
    Circle,
    OrientedRectangle,
    Polygon,
    Rectangle,
)
from barfight.physics.primitives.gjk2 import epa, gjk


@pytest.mark.parametrize(
    "test_shape1,test_shape2",
    [
        (
            Rectangle(Vec2(0, 0), Vec2(1, 1)),
            Rectangle(Vec2(0.5, 0), Vec2(1, 1)),
        ),  # overlapping
        # (
        #     Rectangle(Vec2(0, 0), Vec2(1.0001, 1)),
        #     Rectangle(Vec2(1, 1), Vec2(1, 1)),
        # ),  # edge, fails, collision too small?
        (
            OrientedRectangle(Vec2(0, 0), Vec2(5, 5), 45),
            OrientedRectangle(Vec2(0.5, 0), Vec2(5, 5), 45),
        ),
        (
            Polygon([Vec2(-1, -1), Vec2(0, 1), Vec2(1, -1)]),
            Polygon([Vec2(-1, 1), Vec2(1, 1), Vec2(0, -1)]),
        ),
    ],
)
def test_colliding_intersection(test_shape1, test_shape2):
    result = gjk(test_shape1, test_shape2)

    assert None is not result


@pytest.mark.parametrize(
    "test_shape1,test_shape2",
    [
        (Rectangle(Vec2(0, 0), Vec2(1, 1)), Rectangle(Vec2(0, 2), Vec2(1, 1))),
        # (Circle(Vec2(0, 0), 1), Circle(Vec2(10, 0), 1)),
        (
            OrientedRectangle(Vec2(0, 0), Vec2(5, 5), 45),
            OrientedRectangle(Vec2(10, 10), Vec2(5, 5), 45),
        ),
        (
            Polygon([Vec2(-1, -1), Vec2(0, 1), Vec2(1, -1)]),
            Polygon([Vec2(10, 10), Vec2(10.5, 11), Vec2(11, 10)]),
        ),
        # (Point(Vec2(0, 0)), Point(Vec2(1, 0))),
    ],
)
def test_colliding_no_intersection(test_shape1, test_shape2):
    result = gjk(test_shape1, test_shape2)

    assert None is result


@pytest.mark.parametrize(
    "test_shape1,test_shape2,expected_normal,expected_depth",
    [
        (
            Rectangle(Vec2(0, 0), Vec2(1, 1)),
            Rectangle(Vec2(0.5, 0), Vec2(1, 1)),
            Vec2(1, 0),
            0.5,
        ),
        (
            Circle(Vec2(0, 0), 0.5),
            Circle(Vec2(0.5, 0), 0.5),
            Vec2(1, 0),
            0.5,
        ),  # overlapping
        # (Circle(Vec2(0, 0), 1), Circle(Vec2(2, 0), 1), Vec2(1, 0), 0),  # edge, doesn't work, GJK doesn't see collision
        (
            OrientedRectangle(Vec2(0, 0), Vec2(5, 5), radians(45)),
            OrientedRectangle(Vec2(x=5, y=5), Vec2(5, 5), radians(45)),
            Vec2(1, 1).normalize(),
            2.9289321881345254,
        ),
        # Shapes from dyn4j article: https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/
        (
            Polygon([Vec2(4, 5), Vec2(4, 11), Vec2(9, 9)]),
            Polygon([Vec2(7, 3), Vec2(5, 7), Vec2(12, 7), Vec2(10, 2)]),
            Vec2(0.62, -0.78),
            0.93,
        ),
    ],
)
def test_penetration(test_shape1, test_shape2, expected_normal, expected_depth):
    a, b, c = gjk(test_shape1, test_shape2)
    result = epa(test_shape1, test_shape2, a, b, c)

    assert pytest.approx(expected_normal.x, rel=1e-1, abs=1e-1) == result.normal.x
    assert pytest.approx(expected_normal.y, rel=1e-1, abs=1e-1) == result.normal.y
    assert pytest.approx(expected_depth, rel=1e-2, abs=1e-2) == result.depth


# def test_closest_edge():
#     p = [Vec2(-1, -1), Vec2(-1, 1), Vec2(3, 1), Vec2(3, -1)]
#     edge = closest_edge(p)

#     assert edge is not None


def test_gjk_again():
    points1 = Polygon([Vec2(4, 5), Vec2(4, 11), Vec2(9, 9)])
    points2 = Polygon([Vec2(7, 3), Vec2(5, 7), Vec2(12, 7), Vec2(10, 2)])
    a, b, c = [Vec2(4, 2), Vec2(-8, -2), Vec2(-1, -2)]

    result = epa(points1, points2, a, b, c)

    assert result is not None


# @pytest.mark.xfail(reason="GJK detects collision, but EPA doesn't find a depth")
def test_epa_no_depth():
    r1 = Rectangle(origin=Vec2(x=250.0, y=141.90910799981793), size=Vec2(x=100, y=100))
    r2 = Rectangle(origin=Vec2(x=350.0, y=150.0), size=Vec2(x=100, y=100))

    a, b, c = gjk(r1, r2)
    assert a is not None
    assert b is not None
    assert c is not None

    p = epa(r1, r2, a, b, c)
    assert p.distance != 0.0


def test_epa_incorrect_penetration():
    r1 = Rectangle(
        origin=Vec2(x=250.0001, y=160.00352400002157), size=Vec2(x=100, y=100)
    )
    r2 = Rectangle(origin=Vec2(x=350.0, y=150.0), size=Vec2(x=100, y=100))

    a, b, c = gjk(r1, r2)
    assert a is not None
    assert b is not None
    assert c is not None

    p = epa(r1, r2, a, b, c)

    assert p.depth < 25
