import pytest
from pyglet.math import Vec2

from barfight.physics import Body, Point, QuadTree, Rectangle


def test_rectangle_contains_point():
    r = Rectangle(Vec2(0, 0), Vec2(10, 10))

    assert r.contains_point(Point(Vec2(5, 5)))


def test_rectangle_doesnt_contain_point():
    r = Rectangle(Vec2(0, 0), Vec2(10, 10))

    assert not r.contains_point(Point(Vec2(15, 15)))


def test_quadtree_insert_not_in_boundary():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(1, 1)), 10)
    result = q.insert(Body(Rectangle(Vec2(10, 10), Vec2(11, 11))))

    assert False is result


def test_quadtree_inserts_in_boundary():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 10)
    result = q.insert(Body(Rectangle(Vec2(1, 1), Vec2(2, 2))))

    assert True is result


def test_quadtree_subdivide():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(100, 100)), 10)
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
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 2)

    result1 = q.insert(Body(Rectangle(Vec2(1, 1), Vec2(2, 2))))
    assert False is q.is_divided
    assert True is result1

    result2 = q.insert(Body(Rectangle(Vec2(1, 1), Vec2(2, 2))))
    assert False is q.is_divided
    assert True is result2

    result3 = q.insert(Body(Rectangle(Vec2(1, 1), Vec2(2, 2))))
    assert True is result3
    assert True is q.is_divided
    assert [] == q.bodies


def test_quadtree_subdivide_keeps_big_bodies():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 10)
    big_body = Body(Rectangle(Vec2(1, 1), Vec2(9, 9)))
    q.insert(big_body)
    q.subdivide()

    assert [big_body] == q.bodies


def test_quadtree_subdivide_reinserts_bodies():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 2)
    bottom_left_body = Body(Rectangle(Vec2(0, 0), Vec2(1, 1)))
    bottom_right_body = Body(Rectangle(Vec2(9, 0), Vec2(10, 1)))
    top_right_body = Body(Rectangle(Vec2(9, 9), Vec2(10, 10)))
    top_left_body = Body(Rectangle(Vec2(0, 9), Vec2(1, 10)))
    q.insert(bottom_left_body)
    q.insert(bottom_right_body)
    q.insert(top_right_body)
    q.insert(top_left_body)

    q.insert(Body(Rectangle()))

    assert bottom_left_body in q.bottom_left.bodies
    assert bottom_right_body in q.bottom_right.bodies
    assert top_right_body in q.top_right.bodies
    assert top_left_body in q.top_left.bodies


@pytest.mark.parametrize(
    "rect",
    [
        Rectangle(Vec2(1, 1), Vec2(2, 2)),
        Rectangle(Vec2(8, 1), Vec2(9, 2)),
        Rectangle(Vec2(1, 8), Vec2(2, 9)),
        Rectangle(Vec2(8, 8), Vec2(9, 9)),
    ],
)
def test_quadtree_inserts_into_subdivision(rect):
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 1)
    q.insert(Body(Rectangle()))
    result = q.insert(Body(rect))

    assert True is result


def test_quadtree_insert_doesnt_fit_in_subdivisions():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 1)
    q.insert(Body(Rectangle()))
    result = q.insert(Body(Rectangle(Vec2(1, 1), Vec2(9, 9))))

    assert True is result


def test_quadtree_inserts_when_depth_0():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 10, 0)
    body = Body(Rectangle(Vec2(1, 1), Vec2(9, 9)))
    result = q.insert(body)

    assert True is result
    assert [body] == q.bodies


def test_quadtree_query_bodies_in_parent():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 10, 0)
    body = Body(Rectangle(Vec2(1, 1), Vec2(9, 9)))
    q.insert(body)
    result = q.query(Rectangle(Vec2(1, 1), Vec2(2, 2)))

    assert [body] == result


def test_quadtree_nearest():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 10, 0)
    body = Body(Rectangle(Vec2(8, 8), Vec2(9, 9)))
    q.insert(body)
    p = Point(Vec2(4, 4))
    distance, nearest_body = q.nearest(Point(Vec2(4, 4)))

    assert p.position.distance(body.rectangle.center) == distance
    assert body is nearest_body


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (Point(Vec2(0, 0)), Rectangle(Vec2(1, 1), Vec2(2, 2))),
        (Point(Vec2(10, 0)), Rectangle(Vec2(8, 1), Vec2(9, 2))),
        (Point(Vec2(0, 10)), Rectangle(Vec2(1, 8), Vec2(2, 9))),
        (Point(Vec2(10, 10)), Rectangle(Vec2(8, 8), Vec2(9, 9))),
    ],
)
def test_quadtree_nearest_in_subdivision(test_input, expected):
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 3, 0)
    q.insert(Body(Rectangle(Vec2(1, 1), Vec2(2, 2))))
    q.insert(Body(Rectangle(Vec2(8, 1), Vec2(9, 2))))
    q.insert(Body(Rectangle(Vec2(1, 8), Vec2(2, 9))))
    q.insert(Body(Rectangle(Vec2(8, 8), Vec2(9, 9))))
    distance, nearest_body = q.nearest(test_input)

    assert test_input.position.distance(expected.center) == distance
    assert expected == nearest_body.rectangle


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


def test_quadtree_no_collisions_in_different_subdivisions():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(100, 100)), 1)
    body1 = Body(Rectangle(Vec2(2, 2), Vec2(1, 10)))
    q.insert(body1)
    q.insert(Body(Rectangle(Vec2(1.10, 1.10), Vec2(1.10, 1.10))))
    q.insert(Body(Rectangle(Vec2(1.11, 1.11), Vec2(1.11, 1.11))))
    result = q.collisions([])

    assert [] == result


def test_quadtree_colliding_with():
    q = QuadTree(Rectangle(Vec2(0, 0), Vec2(10, 10)), 4)
    colliding1 = Body(Rectangle(Vec2(1, 1), Vec2(2, 2)))
    colliding2 = Body(Rectangle(Vec2(1.5, 1.5), Vec2(2.5, 2.5)))
    not_colliding = Body(Rectangle(Vec2(5, 5), Vec2(6, 6)))
    q.insert(colliding1)
    q.insert(colliding2)
    q.insert(not_colliding)
    result = q.colliding_with_body(colliding1)

    assert {colliding2} == result


def test_quadtree_collding_with_in_subdivisions():
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
    result = q.colliding_with_body(colliding1)

    assert {colliding2} == result
