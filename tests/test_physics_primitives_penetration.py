from pyglet.math import Vec2

from barfight.physics.primitives import Circle, OrientedRectangle, Polygon


def test_circle_penetrtaion():
    c1 = Circle(Vec2(0, 0), 0.5)
    c2 = Circle(Vec2(0.5, 0), 0.5)

    collision = c1.penetration(c2)

    assert Vec2(0.5, 0) == collision.penetration
    assert 0.5 == collision.depth


def test_polygon_point_penetration():
    p = Polygon([Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1)])
    point = Vec2(0.5, 0.5)

    collision = p.penetration(point)

    assert Vec2(0, 0.5) == collision.penetration
    assert 0.5 == collision.depth


def test_oriented_rectangle_penetration():
    o1 = OrientedRectangle(Vec2(0.5, 0.5), Vec2(0.5, 0.5), 0)
    o2 = OrientedRectangle(Vec2(1, 0), Vec2(0.5, 0.5), 0)

    collision = o1.penetration(o2)

    assert collision.penetration == Vec2(0.5, 0)
    assert collision.depth == 0.5
