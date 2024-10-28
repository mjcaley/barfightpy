from pyglet.math import Vec2

from barfight.physics.primitives import (
    Circle,
    Line,
    LineSegment,
    OrientedRectangle,
    Rectangle,
    circle_circle_collision,
    circle_line_collision,
    circle_lineseg_collision,
    circle_oriented_rectangle_collision,
    circle_point_collision,
    circle_rectangle_collision,
    line_line_collision,
    line_line_segment_collision,
    line_oriented_rectangle_collision,
    line_point_collision,
    line_segment_oriented_rectangle_collision,
    line_segment_point_collision,
    lineseg_lineseg_collision,
    oriented_rect_oriented_rect_collision,
    oriented_rectangle_point_collision,
    point_point_collision,
    rect_rect_collision,
    rectangle_line_collision,
    rectangle_lineseg_collision,
    rectangle_oriented_rectangle_collision,
    rectangle_point_collision,
)


def test_rect_rect_collision():
    a = Rectangle(Vec2(1, 1), Vec2(4, 4))
    b = Rectangle(Vec2(2, 2), Vec2(5, 5))
    c = Rectangle(Vec2(6, 4), Vec2(4, 2))

    assert rect_rect_collision(a, b)
    assert rect_rect_collision(b, c)
    assert not rect_rect_collision(a, c)


def test_circle_circle_collision():
    a = Circle(Vec2(4, 4), 2)
    b = Circle(Vec2(7, 4), 2)
    c = Circle(Vec2(10, 4), 2)

    assert circle_circle_collision(a, b)
    assert circle_circle_collision(b, c)


def test_point_point_collision():
    a = Vec2(2, 3)
    b = Vec2(2, 3)
    c = Vec2(3, 4)

    assert point_point_collision(a, b)
    assert not point_point_collision(a, c)
    assert not point_point_collision(b, c)


def test_line_line_collision():
    up = Vec2(5, 2)
    down = Vec2(5, -1)
    line1 = Line(Vec2(3, 5), down)
    line2 = Line(Vec2(3, 5), up)
    line3 = Line(Vec2(3, 2), up)
    line4 = Line(Vec2(8, 4), down)

    assert line_line_collision(line1, line2)
    assert line_line_collision(line1, line3)
    assert not line_line_collision(line2, line3)
    assert line_line_collision(line1, line4)


def test_lineseg_lineseg_collision():
    s1 = LineSegment(Vec2(3, 4), Vec2(11, 1))
    s2 = LineSegment(Vec2(8, 4), Vec2(11, 7))

    assert not lineseg_lineseg_collision(s1, s2)


def test_oriented_rect_collision():
    o1 = OrientedRectangle(Vec2(0, 0), Vec2(1, 2), 0)
    o2 = OrientedRectangle(Vec2(1, 2), Vec2(1, 2), 45)
    o3 = OrientedRectangle(Vec2(5, 5), Vec2(1, 2), 0)

    assert oriented_rect_oriented_rect_collision(o1, o2)
    assert not oriented_rect_oriented_rect_collision(o1, o3)


def test_circle_point_collision():
    c = Circle(Vec2(6, 4), 3)
    p1 = Vec2(8, 3)
    p2 = Vec2(11, 7)

    assert circle_point_collision(c, p1)
    assert not circle_point_collision(c, p2)


def test_circle_line_collision():
    c = Circle(Vec2(6, 3), 2)
    l = Line(Vec2(4, 7), Vec2(5, -1))

    assert not circle_line_collision(c, l)


def test_circle_lineseg_collision():
    c = Circle(Vec2(4, 4), 3)
    l = LineSegment(Vec2(8, 6), Vec2(13, 6))

    assert not circle_lineseg_collision(c, l)


def test_circle_rectangle_collision():
    r = Rectangle(Vec2(3, 2), Vec2(6, 4))
    c1 = Circle(Vec2(5, 4), 1)
    c2 = Circle(Vec2(7, 8), 1)

    assert circle_rectangle_collision(c1, r)
    assert not circle_rectangle_collision(c2, r)


def test_circle_oriented_rectangle_collision():
    r = OrientedRectangle(Vec2(5, 4), Vec2(3, 2), 30)
    c = Circle(Vec2(5, 7), 2)

    assert circle_oriented_rectangle_collision(c, r)


def test_rectangle_point_collision():
    r = Rectangle(Vec2(3, 2), Vec2(6, 4))
    p = Vec2(4, 5)

    assert rectangle_point_collision(r, p)


def test_rectangle_line_collision():
    assert rectangle_line_collision(
        Rectangle(Vec2(3, 2), Vec2(6, 4)), Line(Vec2(6, 8), Vec2(2, -3))
    )


def test_rectangle_line_segment_collision():
    r = Rectangle(Vec2(3, 2), Vec2(6, 4))
    s = LineSegment(Vec2(6, 8), Vec2(10, 2))

    assert rectangle_lineseg_collision(r, s)


def test_rectangle_oriented_rectangle_collision():
    r = Rectangle(Vec2(1, 5), Vec2(3, 3))
    o = OrientedRectangle(Vec2(10, 4), Vec2(4, 2), 25)

    assert not rectangle_oriented_rectangle_collision(r, o)

    r2 = Rectangle(Vec2(1, 5), Vec2(3, 3))
    o2 = OrientedRectangle(Vec2(1, 5), Vec2(4, 2), 25)

    assert rectangle_oriented_rectangle_collision(r2, o2)

    r3 = Rectangle(Vec2(-5, -5), Vec2(5, 5))
    o3 = OrientedRectangle(Vec2(0, -20), Vec2(5, 5), 45)

    assert not rectangle_oriented_rectangle_collision(r3, o3)


def test_line_point_collision():
    p = Vec2(5, 3)
    l = Line(Vec2(3, 7), Vec2(7, -2))

    assert not line_point_collision(l, p)


def test_line_segment_point_collision():
    p = Vec2(1, 4)
    s = LineSegment(Vec2(6, 6), Vec2(13, 4))

    assert not line_segment_point_collision(s, p)


def test_oriented_rectangle_point_collision():
    o = OrientedRectangle(Vec2(5, 4), Vec2(3, 2), 30)
    p1 = Vec2(6, 5)
    p2 = Vec2(10, 6)

    assert oriented_rectangle_point_collision(o, p1)
    assert not oriented_rectangle_point_collision(o, p2)


def test_line_line_segment_collision():
    s = LineSegment(Vec2(8, 4), Vec2(11, 7))
    l = Line(Vec2(3, 4), Vec2(4, -2))

    assert not line_line_segment_collision(l, s)


def test_line_oriented_rectangle_collision():
    l = Line(Vec2(7, 3), Vec2(2, -1))
    o = OrientedRectangle(Vec2(5, 4), Vec2(3, 2), 30)

    assert line_oriented_rectangle_collision(l, o)


def test_line_segment_oriented_rectangle_collision():
    s = LineSegment(Vec2(1, 8), Vec2(7, 5))
    o = OrientedRectangle(Vec2(5, 4), Vec2(3, 2), 30)

    assert line_segment_oriented_rectangle_collision(s, o)
