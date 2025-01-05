from math import inf
from typing import Iterator

from pyglet.math import Vec2

from .objects import Collision, Line, LineSegment, Rectangle


def overlapping(min_a: float, max_a: float, min_b: float, max_b: float) -> bool:
    return min_b < max_a and min_a < max_b


def is_parallel_line(a: Vec2, b: Vec2) -> bool:
    return 0 == a.rotate90().dot(b)


def equivalent_lines(a: Line, b: Line) -> bool:
    if not is_parallel_line(a.direction, b.direction):
        return False

    subtracted = a.base - b.base
    return is_parallel_line(subtracted, a.direction)


def on_one_side(axis: Line, segment: LineSegment) -> bool:
    d1 = segment.point1 - axis.base
    d2 = segment.point2 - axis.base
    n = (axis.direction).rotate90()

    return n.dot(d1) * n.dot(d2) > 0


def project_vector(project: Vec2, onto: Vec2) -> Vec2:
    dot_onto = onto.dot(onto)
    if 0 < dot_onto:
        dot_project = project.dot(onto)
        return onto * (dot_project / dot_onto)

    return onto


def project_segment(segment: LineSegment, onto: Vec2) -> tuple[float, float]:
    onto.normalize()
    minimum = onto.dot(segment.point1)
    maximum = onto.dot(segment.point2)

    return min(minimum, maximum), max(minimum, maximum)


def project_vertices(vertices: Iterator[Vec2], axis: Vec2) -> tuple[float, float]:
    min_proj = inf
    max_proj = -inf

    for vertex in vertices:
        projection = vertex.dot(axis)
        min_proj = min(min_proj, projection)
        max_proj = max(max_proj, projection)

    return min_proj, max_proj


def min_max_vertex(axis: Vec2, vertices: list[Vec2]) -> tuple[Vec2, Vec2]:
    this_min = inf
    this_max = -inf
    for vertex in vertices:
        distance = vertex.dot(axis)
        if distance < this_min:
            this_min = distance
        if distance > this_max:
            this_max = distance

    return this_min, this_max


def clamp(value: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(value, minimum))


def clamp_rectangle(point: Vec2, rectangle: Rectangle) -> Vec2:
    return Vec2(
        clamp(point.x, rectangle.origin.x, rectangle.origin.x + rectangle.size.x),
        clamp(point.y, rectangle.origin.y, rectangle.origin.y + rectangle.size.y),
    )


def reverse_collision(collision: Collision | None) -> Collision | None:
    if collision:
        return Collision(collision.penetration.rotate180(), collision.depth)

    return None


def convex_hull(vertices: list[Vec2]) -> list[Vec2]:
    if len(vertices) < 3:
        raise ValueError("Convex hull requires at least 3 vertices.")

    sorted_vertices = sorted(vertices, key=lambda vertex: tuple(vertex))
    lower = []
    for vertex in sorted_vertices:
        while (
            len(lower) >= 2 and (lower[-1] - lower[-2]).cross(vertex - lower[-1]) <= 0
        ):
            lower.pop()
        lower.append(vertex)

    upper = []
    for vertex in reversed(sorted_vertices):
        while (
            len(upper) >= 2 and (upper[-1] - upper[-2]).cross(vertex - upper[-1]) <= 0
        ):
            upper.pop()
        upper.append(vertex)

    return lower[:-1] + upper[:-1]
