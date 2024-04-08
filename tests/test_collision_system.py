import pytest
from barfight.components import BoxCollider
from barfight.systems.collision import CollisionSystem, AABB

from pyglet.math import Vec2


@pytest.mark.skip
def test_point_collision():
    aabb = AABB(0, 0, 10, 10)
    collider = BoxCollider(10, 10)
    target = Vec2(-1, -1)

    result = CollisionSystem.test_point(aabb, target)

    assert aabb is result.aabb
    assert Vec2(-1, -5) == result.position  # push point up
    assert Vec2(0, -1) == result.normal     # push point up
    assert Vec2(0, -4) == result.delta      # move from push out point back to colliding point
    assert 0 == result.time                 # instantly, so zero


@pytest.mark.skip
def test_segment_intersection():
    aabb = AABB(0, 0, 10, 10)
    collider = BoxCollider(10, 10)
    position = Vec2(-10, 0)
    delta = Vec2(0, 0)

    hit = CollisionSystem.intersect_segment(aabb, position, delta)

    assert aabb is hit.aabb
    assert Vec2(-1, 0) == hit.normal
    assert Vec2(-5, 0) == hit.position
    assert 0 == hit.time


def test_collision():
    first = AABB(Vec2(1, 0), Vec2(5, 5))
    second = AABB(Vec2(-1, 0), Vec2(5, 5))
    difference = first.minkowski_difference(second)
    penetration = difference.closest_point_on_bounds_to_point(Vec2(0, 0))
    second.center += penetration

    assert Vec2(2, 0) == difference.center
    assert Vec2(10, 10) == difference.extents
    assert Vec2(-8, 0) == penetration
    assert Vec2(-9, 0) == second.center
