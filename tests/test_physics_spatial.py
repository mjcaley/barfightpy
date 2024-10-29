import pytest
from pyglet.math import Vec2

from barfight.physics.body import Body
from barfight.physics.primitives import Rectangle
from barfight.physics.raycast import Ray
from barfight.physics.shapes import RectangleShape
from barfight.physics.spatial import QuadTree


def test_quadtree_insert_not_in_boundary():
    bodies = [Body(RectangleShape(Vec2(10, 10), Vec2(11, 11)))]
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(1, 1)), 10)
    result = q.insert(0)

    assert False is result


def test_quadtree_inserts_in_boundary():
    bodies = [Body(RectangleShape(Vec2(1, 1), Vec2(2, 2)))]
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(10, 10)), 10)
    result = q.insert(0)

    assert True is result


def test_quadtree_subdivide():
    q = QuadTree([], Rectangle(Vec2(0, 0), Vec2(100, 100)), 10)
    q.subdivide()

    assert True is q.is_divided
    assert Rectangle(Vec2(0, 0), Vec2(50, 50)) == q.bottom_left.boundary
    assert 7 == q.bottom_left.depth
    assert Rectangle(Vec2(50, 0), Vec2(100, 50)) == q.bottom_right.boundary
    assert 7 == q.bottom_right.depth
    assert Rectangle(Vec2(0, 50), Vec2(50, 100)) == q.top_left.boundary
    assert 7 == q.top_left.depth
    assert Rectangle(Vec2(50, 50), Vec2(100, 100)) == q.top_right.boundary
    assert 7 == q.top_right.depth


def test_quadtree_subdivides_at_capacity():
    bodies = []
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(10, 10)), 2)

    bodies.append(Body(RectangleShape(Vec2(1, 1), Vec2(2, 2))))
    result1 = q.insert(0)
    assert False is q.is_divided
    assert True is result1

    bodies.append(Body(RectangleShape(Vec2(1, 1), Vec2(2, 2))))
    result2 = q.insert(1)
    assert False is q.is_divided
    assert True is result2

    bodies.append(Body(RectangleShape(Vec2(1, 1), Vec2(2, 2))))
    result3 = q.insert(2)
    assert True is result3
    assert True is q.is_divided
    assert set() == q.children


def test_quadtree_subdivide_keeps_big_bodies():
    bodies = []
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(10, 10)), 10)
    big_body = Body(RectangleShape(Vec2(1, 1), Vec2(8, 8)))
    bodies.append(big_body)
    q.insert(0)
    q.subdivide()

    assert {0} == q.children


def test_quadtree_subdivide_reinserts_bodies():
    bodies = []
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(10, 10)), 2)
    bottom_left_body = Body(RectangleShape(Vec2(0, 0), Vec2(1, 1)))
    bottom_right_body = Body(RectangleShape(Vec2(9, 0), Vec2(1, 1)))
    top_right_body = Body(RectangleShape(Vec2(9, 9), Vec2(1, 1)))
    top_left_body = Body(RectangleShape(Vec2(0, 9), Vec2(1, 1)))
    bodies.append(bottom_left_body)
    q.insert(0)
    bodies.append(bottom_right_body)
    q.insert(1)
    bodies.append(top_right_body)
    q.insert(2)
    bodies.append(top_left_body)
    q.insert(3)

    bodies.append(Body(RectangleShape()))
    q.insert(4)

    assert 0 in q.bottom_left.children
    assert 1 in q.bottom_right.children
    assert 2 in q.top_right.children
    assert 3 in q.top_left.children


@pytest.mark.parametrize(
    "rect",
    [
        Rectangle(Vec2(1, 1), Vec2(1, 1)),
        Rectangle(Vec2(8, 1), Vec2(1, 1)),
        Rectangle(Vec2(1, 8), Vec2(1, 1)),
        Rectangle(Vec2(8, 8), Vec2(1, 1)),
    ],
)
def test_quadtree_inserts_into_subdivision(rect):
    bodies = []
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(10, 10)), 1)
    bodies.append(Body(RectangleShape()))
    q.insert(0)
    bodies.append(Body(RectangleShape(rect.origin, rect.size)))
    result = q.insert(1)

    assert True is result


def test_quadtree_insert_doesnt_fit_in_subdivisions():
    bodies = []
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(10, 10)), 1)
    bodies.append(Body(RectangleShape()))
    q.insert(0)
    bodies.append(Body(RectangleShape(Vec2(1, 1), Vec2(8, 8))))
    result = q.insert(1)

    assert True is result


def test_quadtree_inserts_when_depth_0():
    bodies = []
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(10, 10)), 10, 0)
    body = Body(RectangleShape(Vec2(1, 1), Vec2(8, 8)))
    bodies.append(body)
    result = q.insert(0)

    assert True is result
    assert {0} == q.children


def test_quadtree_query_bodies_in_parent():
    bodies = []
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(10, 10)), 10, 0)
    body = Body(RectangleShape(Vec2(1, 1), Vec2(8, 8)))
    bodies.append(body)
    q.insert(0)
    result = q.query(Rectangle(Vec2(1, 1), Vec2(1, 1)))

    assert [body] == result


def test_quadtree_nearest():
    bodies = []
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(10, 10)), 10, 0)
    body = Body(RectangleShape(Vec2(8, 8), Vec2()))
    bodies.append(body)
    q.insert(0)
    p = Vec2(4, 4)
    distance, nearest_body = q.nearest(p)

    assert p.distance(body.shape.boundary().origin + body.shape.boundary().size / 2) == pytest.approx(distance)
    assert body is nearest_body


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (Vec2(0, 0), Rectangle(Vec2(1, 1), Vec2(1, 1))),
        (Vec2(10, 0), Rectangle(Vec2(8, 1), Vec2(1, 1))),
        (Vec2(0, 10), Rectangle(Vec2(1, 8), Vec2(1, 1))),
        (Vec2(10, 10), Rectangle(Vec2(8, 8), Vec2(1, 1))),
    ],
)
def test_quadtree_nearest_in_subdivision(test_input, expected):
    bodies = []
    q = QuadTree(bodies, Rectangle(Vec2(0, 0), Vec2(10, 10)), 3, 0)
    bodies.append(Body(RectangleShape(Vec2(1, 1), Vec2(1, 1))))
    q.insert(0)
    bodies.append(Body(RectangleShape(Vec2(8, 1), Vec2(1, 1))))
    q.insert(1)
    bodies.append(Body(RectangleShape(Vec2(1, 8), Vec2(1, 1))))
    q.insert(2)
    bodies.append(Body(RectangleShape(Vec2(8, 8), Vec2(1, 1))))
    q.insert(3)
    distance, nearest_body = q.nearest(test_input)

    expected_center = expected.origin + expected.size / 2
    ray_hit = Ray(test_input, expected_center - test_input).intersects(expected)
    assert test_input.distance(ray_hit) == pytest.approx(distance)
    assert expected == nearest_body.shape.primitive


def test_quadtree_collisions():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 4)
    colliding1 = Body(Rectangle(Vec2(1, 1), Vec2(2, 2)))
    colliding2 = Body(Rectangle(Vec2(1.5, 1.5), Vec2(2.5, 2.5)))
    not_colliding = Body(Rectangle(Vec2(5, 5), Vec2(6, 6)))
    q.insert(colliding1)
    q.insert(colliding2)
    q.insert(not_colliding)
    result = q.collisions([])

    assert not_colliding is not result[0][0]
    assert not_colliding is not result[0][1]
    assert (colliding1, colliding2) == result[0] or (colliding2, colliding1) == result[
        0
    ]


def test_quadtree_collisions_in_subdivisions():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(100, 100)), 4)
    colliding1 = Body(Rectangle(Vec2(1, 1), Vec2(2, 2)))
    colliding2 = Body(Rectangle(Vec2(1.5, 1.5), Vec2(2.5, 2.5)))
    not_colliding1 = Body(Rectangle(Vec2(5, 5), Vec2(5, 5)))
    not_colliding2 = Body(Rectangle(Vec2(5.1, 5.1), Vec2(5.1, 5.1)))
    not_colliding3 = Body(Rectangle(Vec2(5.2, 5.2), Vec2(5.2, 5.2)))
    not_colliding4 = Body(Rectangle(Vec2(5.3, 5.3), Vec2(5.3, 5.3)))
    q.insert(colliding1)
    q.insert(colliding2)
    q.insert(not_colliding1)
    q.insert(not_colliding2)
    q.insert(not_colliding3)
    q.insert(not_colliding4)
    result = q.collisions([])

    assert 2 == len(result)
    assert (colliding1, colliding2) == result[0] or (colliding2, colliding1) == result[
        0
    ]


# def test_quadtree_collisions_not_in_same_layer():
#     q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 4)
#     body1 = Body(Rectangle(Vec2(1, 1), Vec2(2, 2)), layer=0b10, mask=0b10)
#     body2 = Body(Rectangle(Vec2(1.5, 1.5), Vec2(2.5, 2.5)), layer=0b1, mask=0b1)
#     q.insert(body1)
#     q.insert(body2)
#     result = q.collisions([])

#     assert [] == result


def test_quadtree_no_collisions_in_different_subdivisions():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(100, 100)), 1)
    body1 = Body(Rectangle(Vec2(2, 2), Vec2(1, 10)))
    q.insert(body1)
    q.insert(Body(Rectangle(Vec2(1.10, 1.10), Vec2(1.10, 1.10))))
    q.insert(Body(Rectangle(Vec2(1.11, 1.11), Vec2(1.11, 1.11))))
    result = q.collisions([])

    assert [] == result
