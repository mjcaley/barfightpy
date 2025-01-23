from math import radians

from pyglet.math import Vec2

from barfight.physics.primitives import (
    Circle,
    Line,
    LineSegment,
    OrientedRectangle,
    Polygon,
    Rectangle,
)
from barfight.physics.primitives.objects import Point


def test_rect_rect_collision():
    a = Rectangle(Vec2(1, 1), Vec2(4, 4))
    b = Rectangle(Vec2(2, 2), Vec2(5, 5))
    c = Rectangle(Vec2(6, 4), Vec2(4, 2))

    assert a.collision(b)
    assert b.collision(c)
    assert not a.collision(c)


def test_circle_circle_collision():
    a = Circle(Vec2(4, 4), 2)
    b = Circle(Vec2(7, 4), 2)
    c = Circle(Vec2(10, 4), 2)

    assert a.collision(b)
    assert b.collision(c)


def test_line_line_collision():
    up = Vec2(5, 2)
    down = Vec2(5, -1)
    line1 = Line(Vec2(3, 5), down)
    line2 = Line(Vec2(3, 5), up)
    line3 = Line(Vec2(3, 2), up)
    line4 = Line(Vec2(8, 4), down)

    assert line1.collision(line2)
    assert line1.collision(line3)
    assert not line2.collision(line3)
    assert line1.collision(line4)


def test_lineseg_lineseg_collision():
    s1 = LineSegment(Vec2(3, 4), Vec2(11, 1))
    s2 = LineSegment(Vec2(8, 4), Vec2(11, 7))

    assert not s1.collision(s2)


def test_oriented_rect_collision():
    o1 = OrientedRectangle(Vec2(0, 0), Vec2(1, 2), radians(0))
    o2 = OrientedRectangle(Vec2(1, 2), Vec2(1, 2), radians(45))
    o3 = OrientedRectangle(Vec2(5, 5), Vec2(1, 2), radians(0))

    assert o1.collision(o2)
    assert not o1.collision(o3)


def test_circle_point_collision():
    c = Circle(Vec2(6, 4), 3)
    p1 = Point(Vec2(8, 3))
    p2 = Point(Vec2(11, 7))

    assert c.collision(p1)
    assert not c.collision(p2)


def test_circle_line_collision():
    circle = Circle(Vec2(6, 3), 2)
    line = Line(Vec2(4, 7), Vec2(5, -1))

    assert not circle.collision(line)


def test_circle_lineseg_collision():
    circle = Circle(Vec2(4, 4), 3)
    line = LineSegment(Vec2(8, 6), Vec2(13, 6))

    assert not circle.collision(line)


def test_circle_rectangle_collision():
    r = Rectangle(Vec2(3, 2), Vec2(6, 4))
    c1 = Circle(Vec2(5, 4), 1)
    c2 = Circle(Vec2(7, 8), 1)

    assert c1.collision(r)
    assert not c2.collision(r)


def test_circle_oriented_rectangle_collision():
    r = OrientedRectangle(Vec2(5, 4), Vec2(3, 2), radians(30))
    c = Circle(Vec2(5, 7), 2)

    assert c.collision(r)


def test_rectangle_point_collision():
    r = Rectangle(Vec2(3, 2), Vec2(6, 4))
    p = Point(Vec2(4, 5))

    assert r.collision(p)


def test_rectangle_line_collision():
    rect = Rectangle(Vec2(3, 2), Vec2(6, 4))
    line = Line(Vec2(6, 8), Vec2(2, -3))
    assert rect.collision(line)


def test_rectangle_line_segment_collision():
    r = Rectangle(Vec2(3, 2), Vec2(6, 4))
    s = LineSegment(Vec2(6, 8), Vec2(10, 2))

    assert r.collision(s)


def test_rectangle_oriented_rectangle_collision():
    r = Rectangle(Vec2(1, 5), Vec2(3, 3))
    o = OrientedRectangle(Vec2(10, 4), Vec2(4, 2), radians(25))

    assert not r.collision(o)

    r2 = Rectangle(Vec2(1, 5), Vec2(3, 3))
    o2 = OrientedRectangle(Vec2(1, 5), Vec2(4, 2), radians(25))

    assert r2.collision(o2)

    r3 = Rectangle(Vec2(-5, -5), Vec2(5, 5))
    o3 = OrientedRectangle(Vec2(0, -20), Vec2(5, 5), radians(45))

    assert not r3.collision(o3)


def test_line_point_collision():
    point = Point(Vec2(5, 3))
    line = Line(Vec2(3, 7), Vec2(7, -2))

    assert not line.collision(point)


def test_line_segment_point_collision():
    p = Point(Vec2(1, 4))
    s = LineSegment(Vec2(6, 6), Vec2(13, 4))

    assert not s.collision(p)


def test_oriented_rectangle_point_collision():
    o = OrientedRectangle(Vec2(5, 4), Vec2(3, 2), radians(30))
    p1 = Point(Vec2(6, 5))
    p2 = Point(Vec2(10, 6))

    assert o.collision(p1)
    assert not o.collision(p2)


def test_line_line_segment_collision():
    seg = LineSegment(Vec2(8, 4), Vec2(11, 7))
    line = Line(Vec2(3, 4), Vec2(4, -2))

    assert not line.collision(seg)


def test_line_oriented_rectangle_collision():
    line = Line(Vec2(7, 3), Vec2(2, -1))
    rect = OrientedRectangle(Vec2(5, 4), Vec2(3, 2), radians(30))

    assert line.collision(rect)


def test_line_segment_oriented_rectangle_collision():
    s = LineSegment(Vec2(1, 8), Vec2(7, 5))
    o = OrientedRectangle(Vec2(5, 4), Vec2(3, 2), radians(30))

    assert s.collision(o)


def test_point_polygon_collision():
    point = Point()
    polygon = Polygon([Vec2(-1, -1), Vec2(-1, 1), Vec2(1, 1), Vec2(1, -1)])

    assert polygon.collision(point)
