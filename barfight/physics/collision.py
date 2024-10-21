from dataclasses import dataclass, field
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


@dataclass
class OrientedRectangle:
    center: Vec2 = field(default_factory=Vec2)
    half_extent: Vec2 = field(default_factory=Vec2)
    rotation: float = 0


def rect_rect_collision(a: Rectangle, b: Rectangle) -> bool:
    return not (
        a.origin.x >= b.size.x
        or a.size.x <= b.origin.x
        or a.origin.y >= b.size.y
        or a.size.y <= b.origin.y
    )


def circle_circle_collision(a: Circle, b: Circle) -> bool:
    radius_sum = a.radius + b.radius
    distance = a.center.distance(b.center)
    return distance <= radius_sum


def point_point_collision(a: Vec2, b: Vec2) -> bool:
    return a == b


def rotate90(v: Vec2) -> Vec2:
    return Vec2(-v.y, v.x)


def is_parallel_line(a: Vec2, b: Vec2) -> bool:
    return 0 == rotate90(a).dot(b)


def equivalent_lines(a: Line, b: Line) -> bool:
    if not is_parallel_line(a.direction, b.direction):
        return False
    
    subtracted = a.base - b.base
    return is_parallel_line(subtracted, a.direction)


def line_line_collision(a: Line, b: Line) -> bool:
    if is_parallel_line(a, b):
        return equivalent_lines(a, b)
    else:
        return True


def on_one_side(axis: Line, segment: LineSegment) -> bool:
    d1 = segment.point1 - axis.base
    d2 = segment.point2 - axis.base
    n = rotate90(axis.direction)

    return n.dot(d1) * n.dot(d2) > 0


def project_segment(segment: LineSegment, onto: Vec2) -> tuple[float, float]:
    onto.normalize()
    minimum = onto.dot(segment.point1)
    maximum = onto.dot(segment.point2)
    
    return min(minimum, maximum), max(minimum, maximum)


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
        
        return min_b <= max_a and min_a <= max_b
    else:
        return True
