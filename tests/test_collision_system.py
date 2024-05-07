import pytest
from pyglet.math import Vec2

from barfight.components import BoxCollider, Position
from barfight.systems.collision import AABB, Line, line_rect_intersection, line_vs_rect, point_rect_collides, point_rect_resolve, rect_rect_resolve, rect_vs_rect


def test_point_rect_collides():
    collides = point_rect_collides(Vec2(-1, 0), AABB(0, Position(Vec2(0, 0)), 10, 10))

    assert True is collides


@pytest.mark.parametrize("point,expected", [
    (Vec2(-1, 0), Vec2(-4, 0)),
    (Vec2(1, 0), Vec2(4, 0)),
    (Vec2(0, -1), Vec2(0, -4)),
    (Vec2(0, 1), Vec2(0, 4)),
])
def test_point_rect_resolve(point, expected):
    resolution = point_rect_resolve(point, AABB(0, Position(Vec2(0, 0)), 10, 10))

    assert expected == resolution


def test_rect_vs_rect_collides():
    collides = rect_vs_rect(AABB(0, Position(Vec2(-1, 0)), 10, 10), AABB(1, Position(Vec2(1, 0)), 10, 10))

    assert True is collides


@pytest.mark.parametrize("rect1,rect2,expected", [
    (AABB(0, Position(Vec2(-1, 0)), 10, 10), AABB(1, Position(Vec2(0, 0)), 10, 10), Vec2(-9, 0)), # Collides on left
    (AABB(0, Position(Vec2(1, 0)), 10, 10), AABB(1, Position(Vec2(0, 0)), 10, 10), Vec2(9, 0)),   # Collides on right
    (AABB(0, Position(Vec2(0, -1)), 10, 10), AABB(1, Position(Vec2(0, 0)), 10, 10), Vec2(0, -9)), # Collides on top
    (AABB(0, Position(Vec2(0, 1)), 10, 10), AABB(1, Position(Vec2(0, 0)), 10, 10), Vec2(0, 9)),   # Collides on bottom
])
def test_rect_rect_resolve(rect1: AABB, rect2: AABB, expected: Vec2):
    resolution = rect_rect_resolve(rect1, rect2)

    assert expected == resolution


@pytest.mark.parametrize("line,rect,expected", [
    (Line(Vec2(-2, 0), Vec2(1, 0)), AABB(0, Position(Vec2(0, 0)), 2, 2), 1),
    (Line(Vec2(2, 0), Vec2(-1, 0)), AABB(0, Position(Vec2(0, 0)), 2, 2), 1),
    (Line(Vec2(0, -2), Vec2(0, 1)), AABB(0, Position(Vec2(0, 0)), 2, 2), 1),
    (Line(Vec2(0, 2), Vec2(0, -1)), AABB(0, Position(Vec2(0, 0)), 2, 2), 1),
])
def test_line_vs_rect(line: Line, rect: AABB, expected: float):
    collision = line_vs_rect(line, rect)

    assert expected == collision


def test_line_rect_intersection():
    resolution = line_rect_intersection(Line(Vec2(0, 0), Vec2(1, 0)), 10)

    assert Vec2(10, 0) == resolution
