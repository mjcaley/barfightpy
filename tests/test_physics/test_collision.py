from barfight.physics.collision import Rectangle, rect_rect_collision
from pyglet.math import Vec2


def test_rect_rect_collision():
    assert rect_rect_collision(Rectangle(Vec2(0, 0), Vec2(1, 1)), Rectangle(Vec2(0.5, 0.5), Vec2(1.5, 1.5)))
    assert not rect_rect_collision(Rectangle(Vec2(0, 0), Vec2(1, 1)), Rectangle(Vec2(2, 2), Vec2(3, 3)))


def test_lineseg_lineseg_collision():
    ...
