from pyglet.math import Vec2

from barfight.physics.primitives.objects import Polygon


def test_polygon_is_convex():
    p1 = Polygon([Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1)])
    assert p1.is_convex()

    p2 = Polygon([Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1), Vec2(0.5, 0.5)])
    assert not p2.is_convex()
