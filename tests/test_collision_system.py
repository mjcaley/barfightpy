import pytest
from pyglet.math import Vec2

from barfight import ecs
from barfight import events
from barfight.components import BoxCollider, Position
from barfight.systems import AABB, CollisionSystem, Ray, distance, ray_vs_rect, point_rect_collides, point_rect_resolve, rect_rect_resolve, rect_vs_rect


def test_point_rect_collides():
    collides = point_rect_collides(Vec2(-1, 0), AABB(0, Vec2(0, 0), 10, 10))

    assert True is collides


@pytest.mark.parametrize("point,expected", [
    (Vec2(-1, 0), Vec2(-4, 0)),
    (Vec2(1, 0), Vec2(4, 0)),
    (Vec2(0, -1), Vec2(0, -4)),
    (Vec2(0, 1), Vec2(0, 4)),
])
def test_point_rect_resolve(point, expected):
    resolution = point_rect_resolve(point, AABB(0, Vec2(0, 0), 10, 10))

    assert expected == resolution


def test_rect_vs_rect_collides():
    collides = rect_vs_rect(AABB(0, Vec2(-1, 0), 10, 10), AABB(1, Vec2(1, 0), 10, 10))

    assert True is collides


def test_rect_vs_rect_doesnt_collide():
    assert not rect_vs_rect(AABB(0, Vec2(-10, -10), 10, 10), AABB(1, Vec2(10, 10), 10, 10))


@pytest.mark.parametrize("rect1,rect2,expected", [
    (AABB(0, Vec2(-1, 0), 10, 10), AABB(1, Vec2(0, 0), 10, 10), Vec2(-9, 0)), # Collides on left
    (AABB(0, Vec2(1, 0), 10, 10), AABB(1, Vec2(0, 0), 10, 10), Vec2(9, 0)),   # Collides on right
    (AABB(0, Vec2(0, -1), 10, 10), AABB(1, Vec2(0, 0), 10, 10), Vec2(0, -9)), # Collides on top
    (AABB(0, Vec2(0, 1), 10, 10), AABB(1, Vec2(0, 0), 10, 10), Vec2(0, 9)),   # Collides on bottom
])
def test_rect_rect_resolve(rect1: AABB, rect2: AABB, expected: Vec2):
    resolution = rect_rect_resolve(rect1, rect2)

    assert expected == resolution



@pytest.mark.parametrize("ray_pos,ray_dir,expected", [
    (Vec2(0, 0), Vec2(1, 1), Vec2(1, 1)),
    (Vec2(5, 0), Vec2(-1, 1), Vec2(4, 1)),
    (Vec2(5, 5), Vec2(-1, -1), Vec2(4, 4)),
    (Vec2(0, 5), Vec2(1, -1), Vec2(1, 4)),
])
def test_line_vs_rect2(ray_pos, ray_dir, expected):
    ray = Ray(ray_pos, ray_dir)
    rect = AABB(0, Vec2(2.5, 2.5), 3, 3)
    intersection = ray_vs_rect(ray, rect)

    assert expected == intersection


def test_distance():
    d = distance(Vec2(-5, 0), AABB(0, Vec2(0, 0), 2, 2))

    assert 4 == d


def test_collision_process(ecs_world):
    collision_events = {}
    def collision_callback(source: int, collisions: set[int]):
        collision_events[source] = collisions

    ecs.set_handler(events.COLLISION_EVENT, collision_callback)
    c = CollisionSystem()
    ecs.add_system(c)
    
    colliding1 = ecs.create_entity(Position(Vec2(0, 0)), BoxCollider(height=10, width=10))
    colliding2 = ecs.create_entity(Position(Vec2(0, 0)), BoxCollider(height=10, width=10))
    not_colliding = ecs.create_entity(Position(Vec2(20, 20)), BoxCollider(height=10, width=10))

    ecs.update(0)

    assert colliding1 in collision_events
    assert {colliding2} == collision_events[colliding1]
    assert colliding2 in collision_events
    assert {colliding1} == collision_events[colliding2]
    assert not_colliding not in collision_events
