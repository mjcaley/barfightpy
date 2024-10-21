from barfight.physics.collision import LineSegment, Rectangle, lineseg_lineseg_collision, rect_rect_collision
from pyglet.math import Vec2


def test_rect_rect_collision():
    assert rect_rect_collision(Rectangle(Vec2(0, 0), Vec2(1, 1)), Rectangle(Vec2(0.5, 0.5), Vec2(1.5, 1.5)))
    assert not rect_rect_collision(Rectangle(Vec2(0, 0), Vec2(1, 1)), Rectangle(Vec2(2, 2), Vec2(3, 3)))


def test_lineseg_lineseg_collision():
    s1 = LineSegment(Vec2(3, 4), Vec2(11, 1))
    s2 = LineSegment(Vec2(8, 4), Vec2(11, 7))

    assert not lineseg_lineseg_collision(s1, s2)
