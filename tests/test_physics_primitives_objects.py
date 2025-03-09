from math import radians

import pytest
from pyglet.math import Vec2

from barfight.physics.primitives.objects import (
    Circle,
    OrientedRectangle,
    Point,
    Polygon,
    Rectangle,
)


def test_polygon_is_convex():
    p1 = Polygon([Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1)])
    assert p1.is_convex()

    p2 = Polygon([Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1), Vec2(0.5, 0.5)])
    assert not p2.is_convex()


def test_point_furthest():
    p = Point(Vec2(0, 0))

    assert Vec2(0, 0) == p.furthest(Vec2(1, 1))


def test_circle_furthest():
    c = Circle(Vec2(0, 0), 1)
    expected = Vec2(1, 0).rotate(radians(45))
    result = c.furthest(Vec2(1, 1))

    assert expected.x == pytest.approx(result.x)
    assert expected.y == pytest.approx(result.y)


def test_rectangle_furthest():
    r = Rectangle(Vec2(0, 0), Vec2(1, 1))

    assert Vec2(1, 1) == r.furthest(Vec2(1, 1).normalize())
    assert Vec2(1, 0) == r.furthest(Vec2(1, -1).normalize())
    assert Vec2(0, 0) == r.furthest(Vec2(-1, -1).normalize())
    assert Vec2(0, 1) == r.furthest(Vec2(-1, 1).normalize())


def test_orientedrectangle_furthest():
    o = OrientedRectangle(Vec2(0, 0), Vec2(1, 1), radians(45))

    assert Vec2(-1, -1).rotate(radians(45)) == o.furthest(Vec2(0, -1).normalize())
    assert Vec2(-1, 1).rotate(radians(45)) == o.furthest(Vec2(-1, 0).normalize())
    assert Vec2(1, 1).rotate(radians(45)) == o.furthest(Vec2(0, 1).normalize())
    assert Vec2(1, -1).rotate(radians(45)) == o.furthest(Vec2(1, 0).normalize())
