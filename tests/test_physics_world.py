from math import radians

from pyglet.math import Vec2

from barfight.physics.body import Body, BodyKind
from barfight.physics.raycast import Ray
from barfight.physics.shapes import CircleShape, OrientedRectangleShape, RectangleShape
from barfight.physics.world import CollisionPair, PhysicsWorld


def test_body_added():
    w = PhysicsWorld(Vec2(), Vec2(100, 100))
    b = Body(RectangleShape(Vec2(1, 1), Vec2(1, 1)))
    w.add(b)

    assert b in w.bodies


def test_body_removed():
    w = PhysicsWorld(Vec2(), Vec2(100, 100))
    b = Body(RectangleShape(Vec2(1, 1), Vec2(1, 1)))
    w.add(b)
    w.remove(b)

    assert b not in w.bodies


def test_clear():
    w = PhysicsWorld(Vec2(), Vec2(100, 100))
    b = Body(RectangleShape(Vec2(1, 1), Vec2(1, 1)))
    w.add(b)
    w.clear()

    assert [] == w.bodies
    assert set() == w.active_collisions
    assert set() == w.new_collisions


def test_broad_phase():
    w = PhysicsWorld(Vec2(), Vec2(100, 100))
    b1 = Body(RectangleShape(Vec2(0, 0), Vec2(10, 10)), data=1)
    b2 = Body(RectangleShape(Vec2(5, 5), Vec2(10, 10)), data=2)
    b3 = Body(RectangleShape(Vec2(75, 75), Vec2(10, 10)), data=3)
    w.add(b1)
    w.add(b2)
    w.add(b3)
    collisions = w.broad_phase()

    assert CollisionPair(b1, b2) in collisions
    assert CollisionPair(b2, b1) in collisions
    for collision in collisions:
        assert b3 is not collision.first
        assert b3 is not collision.second


def test_discrete_phase():
    w = PhysicsWorld(Vec2(), Vec2(100, 100))
    b1 = Body(RectangleShape(Vec2(0, 0), Vec2(10, 10)), data=1)
    b2 = Body(RectangleShape(Vec2(5, 5), Vec2(10, 10)), data=2)
    w.add(b1)
    w.add(b2)
    broad_collisions = {CollisionPair(b1, b2), CollisionPair(b2, b1)}
    collisions, resolutions = w.discrete_phase(broad_collisions)

    assert 2 == len(collisions)
    collisions_list = [c for c in collisions]
    if collisions_list[0].first is b1:
        assert b1 is collisions_list[0].first
        assert b2 is collisions_list[0].second
        assert b2 is collisions_list[1].first
        assert b1 is collisions_list[1].second
    else:
        assert b2 is collisions_list[0].first
        assert b1 is collisions_list[0].second
        assert b1 is collisions_list[1].first
        assert b2 is collisions_list[1].second


def test_step():
    w = PhysicsWorld(Vec2(), Vec2(100, 100))
    b1 = Body(RectangleShape(Vec2(0, 0), Vec2(10, 10)), BodyKind.Dynamic, data=1)
    b2 = Body(RectangleShape(Vec2(5, 5), Vec2(10, 10)), BodyKind.Static, data=2)
    w.add(b1)
    w.add(b2)
    w.step(0)

    assert Vec2(5, 0) == b1.shape.position


def test_raycast():
    w = PhysicsWorld(Vec2(), Vec2(100, 100))
    b1 = Body(RectangleShape(Vec2(0, 0), Vec2(10, 10)), BodyKind.Dynamic, data=1)
    b2 = Body(RectangleShape(Vec2(0, 0), Vec2(10, 10)), BodyKind.Static, data=2)
    w.add(b1)
    w.add(b2)
    hit = w.raycast(Ray(Vec2(-1, -1), Vec2(1, 1), 10), BodyKind.Static)

    assert hit is not None
    assert Vec2(0, 0) == hit.point
    assert b2 is hit.body


def test_nearest():
    q = PhysicsWorld(Vec2(0, 0), Vec2(10, 10))
    body = Body(RectangleShape(Vec2(8, 8), Vec2()))
    q.add(body)
    p = Vec2(4, 4)
    nearest_body = q.nearest(p)

    assert nearest_body is not None
    assert body is nearest_body


def test_move_body_rectangles():
    q = PhysicsWorld(Vec2(0, 0), Vec2(100, 100))
    body = Body(RectangleShape(Vec2(1, 1), Vec2(1, 1)), velocity=Vec2(10.0, 0))
    static_body = Body(RectangleShape(Vec2(5, 0), Vec2(10, 10)), BodyKind.Static)
    q.add(body)
    q.add(static_body)
    q.move(10.0)


def test_move_body_rectangle_oriented_rectangle():
    q = PhysicsWorld(Vec2(0, 0), Vec2(100, 100))
    body = Body(RectangleShape(Vec2(50, 50), Vec2(1, 1)), velocity=Vec2(10.0, 0))
    static_body = Body(
        OrientedRectangleShape(Vec2(55, 50), Vec2(5, 5), radians(45)), BodyKind.Static
    )
    q.add(body)
    q.add(static_body)
    q.move(10.0)


def test_time_of_impact():
    q = PhysicsWorld(Vec2(0, 0), Vec2(100, 100))
    body = Body(CircleShape(Vec2(0, 0), 10), velocity=Vec2(10.0, 0))
    static_body = Body(RectangleShape(Vec2(10.5, -10), Vec2(20, 20)), BodyKind.Static)
    q.add(body)
    q.add(static_body)

    result = q.time_of_impact(body, static_body, 0.2)

    assert 0 < result
