from pyglet.math import Vec2

from barfight.physics.primitives import (
    Circle,
    Line,
    LineSegment,
    OrientedRectangle,
    Rectangle,
    circle_circle_collision,
    circle_point_collision,
    line_line_collision,
    lineseg_lineseg_collision,
    oriented_rect_oriented_rect_collision,
    point_point_collision,
    rect_rect_collision,
    rectangle_line_collision,
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


def test_rectangle_line_collision():
    assert rectangle_line_collision(Rectangle(Vec2(3, 2), Vec2(6, 4)), Line(Vec2(6, 8), Vec2(2, -3)))
