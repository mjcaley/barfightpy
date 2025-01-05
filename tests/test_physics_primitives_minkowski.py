from pyglet.math import Vec2

from barfight.physics.primitives import Circle, OrientedRectangle, Polygon, Rectangle


def test_circle_minkowski_difference():
    c1 = Circle(Vec2(0, 0), 0.5)
    c2 = Circle(Vec2(1, 0), 0.5)

    assert Circle(Vec2(-1, 0), 1) == c1.minkowski_difference(c2)


def test_rectangle_minkowski_difference():
    r1 = Rectangle(Vec2(0, 0), Vec2(1, 1))
    r2 = Rectangle(Vec2(1, 0), Vec2(1, 1))

    assert r1.minkowski_difference(r2) == Rectangle(Vec2(-2, -1), Vec2(2, 2))


def test_oriented_rectangle_minkowski_difference():
    o1 = OrientedRectangle(Vec2(0.5, 0.5), Vec2(0.5, 0.5), 0)
    o2 = OrientedRectangle(Vec2(1.5, 0.5), Vec2(0.5, 0.5), 0)

    assert o1.minkowski_difference(o2) == Polygon(
        [
            Vec2(-2, -1),
            Vec2(0, -1),
            Vec2(0, 1),
            Vec2(-2, 1),
        ]
    )


def test_polygon_minkowski_difference():
    p1 = Polygon([Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1)])
    p2 = Polygon([Vec2(1, 0), Vec2(2, 0), Vec2(2, 1), Vec2(1, 1)])

    assert p1.minkowski_difference(p2) == Polygon(
        [
            Vec2(-2, -1),
            Vec2(0, -1),
            Vec2(0, 1),
            Vec2(-2, 1),
        ]
    )
