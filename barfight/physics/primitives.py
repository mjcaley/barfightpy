from dataclasses import dataclass, field
from itertools import chain
from math import cos, inf, radians, sin
from typing import Generator

from pyglet.math import Vec2


@dataclass
class Line:
    base: Vec2 = field(default_factory=Vec2)
    direction: Vec2 = field(default_factory=Vec2)


@dataclass
class LineSegment:
    point1: Vec2 = field(default_factory=Vec2)
    point2: Vec2 = field(default_factory=Vec2)


@dataclass
class Circle:
    center: Vec2 = field(default_factory=Vec2)
    radius: float = 0


@dataclass
class Rectangle:
    origin: Vec2 = field(default_factory=Vec2)
    size: Vec2 = field(default_factory=Vec2)

    @property
    def bottom_left_vertex(self) -> Vec2:
        return self.origin

    @property
    def bottom_right_vertex(self) -> Vec2:
        return Vec2(self.origin.x, self.origin.y + self.size.y)

    @property
    def top_left_vertex(self) -> Vec2:
        return Vec2(self.origin.x, self.origin.y + self.size.y)

    @property
    def top_right_vertex(self) -> Vec2:
        return self.origin + self.size


@dataclass
class OrientedRectangle:
    center: Vec2 = field(default_factory=Vec2)
    half_extent: Vec2 = field(default_factory=Vec2)
    rotation: float = 0

    @property
    def top_right_vertex(self) -> Vec2:
        vertex = (self.half_extent + self.center).rotate(self.rotation) + self.center

        return vertex

    @property
    def bottom_right_vertex(self) -> Vec2:
        vertex = Vec2(self.half_extent.x, self.half_extent.y)
        vertex.x *= -1
        vertex = vertex.rotate(self.rotation) + self.center

        return vertex

    @property
    def bottom_left_vertex(self) -> Vec2:
        vertex = Vec2(self.half_extent.x, self.half_extent.y) * -1
        vertex = vertex.rotate(self.rotation) + self.center

        return vertex

    @property
    def top_left_vertex(self) -> Vec2:
        vertex = Vec2(self.half_extent.x, self.half_extent.y)
        vertex.y *= -1
        vertex = vertex.rotate(self.rotation) + self.center

        return vertex

    def vertices(self) -> Generator[Vec2, None, None]:
        yield self.bottom_left_vertex
        yield self.top_left_vertex
        yield self.top_right_vertex
        yield self.bottom_right_vertex

    def axes(self) -> Generator[Vec2, None, None]:
        yield Vec2(cos(radians(self.rotation)), sin(radians(self.rotation)))
        yield Vec2(cos(radians(self.rotation + 90)), sin(radians(self.rotation + 90)))


# region Utility


def overlapping(min_a: float, max_a: float, min_b: float, max_b: float) -> bool:
    return min_b <= max_a and min_a <= max_b


def rotate90(v: Vec2) -> Vec2:
    return Vec2(-v.y, v.x)


def is_parallel_line(a: Vec2, b: Vec2) -> bool:
    return 0 == rotate90(a).dot(b)


def equivalent_lines(a: Line, b: Line) -> bool:
    if not is_parallel_line(a.direction, b.direction):
        return False

    subtracted = a.base - b.base
    return is_parallel_line(subtracted, a.direction)


def on_one_side(axis: Line, segment: LineSegment) -> bool:
    d1 = segment.point1 - axis.base
    d2 = segment.point2 - axis.base
    n = rotate90(axis.direction)

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


# endregion


def rect_rect_collision(a: Rectangle, b: Rectangle) -> bool:
    a_left = a.origin.x
    a_right = a_left + a.size.x
    b_left = b.origin.x
    b_right = b_left + b.size.x

    a_bottom = a.origin.y
    a_top = a_bottom + a.size.y
    b_bottom = b.origin.y
    b_top = b_bottom + b.size.y

    return overlapping(a_left, a_right, b_left, b_right) and overlapping(
        a_bottom, a_top, b_bottom, b_top
    )


def circle_circle_collision(a: Circle, b: Circle) -> bool:
    radius_sum = a.radius + b.radius
    distance = a.center.distance(b.center)
    return distance <= radius_sum


def point_point_collision(a: Vec2, b: Vec2) -> bool:
    return a == b


def line_line_collision(a: Line, b: Line) -> bool:
    if is_parallel_line(a.direction, b.direction):
        return equivalent_lines(a, b)
    else:
        return True


def lineseg_lineseg_collision(a: LineSegment, b: LineSegment) -> bool:
    axis_a = Line(a.point1, a.point2 - b.point1)
    if on_one_side(axis_a, b):
        return False

    axis_b = Line(b.point1, b.point2 - a.point1)
    if on_one_side(axis_b, a):
        return False

    if is_parallel_line(axis_a.direction, axis_b.direction):
        min_a, max_a = project_segment(a, axis_a.direction)
        min_b, max_b = project_segment(b, axis_b.direction)

        return overlapping(min_a, max_a, min_b, max_b)
    else:
        return True


def oriented_rect_oriented_rect_collision(
    a: OrientedRectangle, b: OrientedRectangle
) -> bool:
    a_vertices = [_ for _ in a.vertices()]
    b_vertices = [_ for _ in b.vertices()]
    for axis in chain(a.axes(), b.axes()):
        a_min, a_max = min_max_vertex(axis, a_vertices)
        b_min, b_max = min_max_vertex(axis, b_vertices)
        if a_max < b_min or b_max < a_min:
            return False

    return True


def circle_point_collision(circle: Circle, point: Vec2) -> bool:
    return circle.center.distance(point) <= circle.radius


def circle_line_collision(circle: Circle, line: Line) -> bool:
    lc = circle.center.distance(line.base)
    projected = project_vector(lc, line.direction)
    nearest = line.base + projected

    return circle_point_collision(circle, nearest)


def circle_lineseg_collision(circle: Circle, line: LineSegment) -> bool:
    if circle_point_collision(circle, line.point1) or circle_point_collision(
        circle, line.point2
    ):
        return True

    line_distance = line.point1.distance(line.point2)
    circle_distance = circle.center.distance(line.point1)
    projected = project_vector(circle_distance, line_distance)
    nearest = line.point1 + projected

    return (
        circle_point_collision(circle, nearest)
        and projected.mag <= line_distance.mag
        and 0 <= projected.dot(line_distance)
    )


def circle_rectangle_collision(circle: Circle, rectangle: Rectangle) -> bool:
    clamped = clamp_rectangle(circle.center, rectangle)
    return circle_point_collision(circle, clamped)


def circle_oriented_rectangle_collision(
    circle: Circle, rectangle: OrientedRectangle
) -> bool:
    local_rect = Rectangle(Vec2(0, 0), rectangle.half_extent * 2)

    distance = circle.center - rectangle.center
    distance.rotate(-rectangle.rotation)
    local_circle = Circle(distance + rectangle.half_extent, circle.radius)

    return circle_rectangle_collision(local_circle, local_rect)


def rectangle_point_collision(rectangle: Rectangle, point: Vec2) -> bool:
    left = rectangle.origin.x
    right = left + rectangle.size.x
    bottom = rectangle.origin.y
    top = bottom + rectangle.size.y

    return left <= point.x and bottom <= point.y and point.x <= right and point.y <= top


def rectangle_line_collision(rectangle: Rectangle, line: Line) -> bool:
    n = rotate90(line.direction)

    corner1 = rectangle.bottom_left_vertex - line.base
    corner2 = rectangle.top_right_vertex - line.base
    corner3 = rectangle.bottom_right_vertex - line.base
    corner4 = rectangle.top_left_vertex - line.base

    dp1 = n.dot(corner1)
    dp2 = n.dot(corner2)
    dp3 = n.dot(corner3)
    dp4 = n.dot(corner4)

    return dp1 * dp2 <= 0 or dp2 * dp3 <= 0 or dp3 * dp4 <= 0
