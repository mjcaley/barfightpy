from dataclasses import dataclass, field
from functools import singledispatchmethod
from itertools import chain, islice, pairwise
from math import cos, inf, pi, radians, sin
from typing import Generator, Iterator, Self

from pyglet.math import Vec2


@dataclass(frozen=True)
class Collision:
    penetration: Vec2
    depth: float


# region Shapes


@dataclass
class Line:
    base: Vec2 = field(default_factory=Vec2)
    direction: Vec2 = field(default_factory=Vec2)

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Vec2 | None:
        raise NotImplementedError

    @property
    def center(self) -> Vec2:
        return self.base


@dataclass
class LineSegment:
    point1: Vec2 = field(default_factory=Vec2)
    point2: Vec2 = field(default_factory=Vec2)

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Vec2 | None:
        raise NotImplementedError

    def edges(self) -> Generator[Self, None, None]:
        yield self

    @property
    def center(self) -> Vec2:
        return (self.point1 + self.point2) / 2


@dataclass
class Circle:
    center: Vec2 = field(default_factory=Vec2)
    radius: float = 0

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Vec2 | None:
        raise NotImplementedError
    
    def vertices(self, num_points = 16) -> Generator[Vec2, None, None]:
        point = self.center + Vec2(self.radius, 0)
        rotation = 2 * pi / num_points
        for _ in range(num_points):
            point = point.rotate(rotation)
            yield point


@dataclass
class Rectangle:
    origin: Vec2 = field(default_factory=Vec2)
    size: Vec2 = field(default_factory=Vec2)

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Vec2 | None:
        raise NotImplementedError

    @property
    def center(self) -> Vec2:
        return self.origin + (self.size / 2)

    @center.setter
    def center(self, value: Vec2):
        self.origin = value - (self.size / 2)

    @property
    def bottom_left_vertex(self) -> Vec2:
        return self.origin

    @property
    def bottom_right_vertex(self) -> Vec2:
        return Vec2(self.origin.x, self.origin.y + self.size.y)

    @property
    def top_left_vertex(self) -> Vec2:
        return Vec2(self.origin.x + self.size.x, self.origin.y)

    @property
    def top_right_vertex(self) -> Vec2:
        return self.origin + self.size

    def vertices(self) -> Generator[Vec2, None, None]:
        yield self.bottom_left_vertex
        yield self.top_left_vertex
        yield self.top_right_vertex
        yield self.bottom_right_vertex

    def edges(self) -> Generator[LineSegment, None, None]:
        for v1, v2 in pairwise(chain(self.vertices(), islice(self.vertices(), 1))):
            yield LineSegment(v1, v2)

    def axes(self) -> Generator[Vec2, None, None]:
        yield Vec2(1, 0)
        yield Vec2(0, 1)


@dataclass
class OrientedRectangle:
    center: Vec2 = field(default_factory=Vec2)
    half_extent: Vec2 = field(default_factory=Vec2)
    rotation: float = 0

    @singledispatchmethod
    def collision(self, any) -> bool:
        raise NotImplementedError

    @singledispatchmethod
    def penetration(self, any) -> Vec2 | None:
        raise NotImplementedError

    @property
    def top_right_vertex(self) -> Vec2:
        vertex = self.half_extent.rotate(self.rotation) + self.center

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

    def edges(self) -> Generator[LineSegment, None, None]:
        for v1, v2 in pairwise(chain(self.vertices(), islice(self.vertices(), 1))):
            yield LineSegment(v1, v2)

    def axes(self) -> Generator[Vec2, None, None]:
        yield Vec2(cos(self.rotation), sin(self.rotation))
        yield Vec2(cos(self.rotation + radians(90)), sin(self.rotation + radians(90)))

    @property
    def bounding_box(self) -> Rectangle:
        min_x = inf
        max_x = -inf
        min_y = inf
        max_y = -inf
        for vertex in self.vertices():
            min_x = min(min_x, vertex.x)
            max_x = max(max_x, vertex.x)
            min_y = min(min_y, vertex.y)
            max_y = max(max_y, vertex.y)

        return Rectangle(Vec2(min_x, min_y), Vec2(max_x - min_x, max_y - min_y))


@dataclass
class Polygon:
    points: list[Vec2]

    def vertices(self) -> Generator[Vec2, None, None]:
        return (point for point in self.points)
    
    def edges(self) -> Generator[LineSegment, None, None]:
        for v1, v2 in pairwise(chain(self.vertices(), islice(self.vertices(), 1))):
            yield LineSegment(v1, v2)

    def axes(self) -> Generator[Vec2, None, None]:
        for edge in self.edges():
            yield rotate90(edge.point2 - edge.point1).normalize()

    @property
    def bounding_box(self) -> Rectangle:
        min_x = inf
        max_x = -inf
        min_y = inf
        max_y = -inf

        for vertex in self.vertices():
            min_x = min(min_x, vertex.x)
            max_x = max(max_x, vertex.x)
            min_y = min(min_y, vertex.y)
            max_y = max(max_y, vertex.y)

        return Rectangle(Vec2(min_x, min_y), Vec2(max_x - min_x, max_y - min_y))
    
    def is_convex(self) -> bool:
        cross = []

        for e1, e2 in pairwise(chain(self.edges(), islice(self.edges(), 1))):
            v1 = e1.point2 - e1.point1
            v2 = e2.point2 - e2.point1
            cross.append(v1.x * v2.y - v1.y * v2.x)

        all_positive = all()


# endregion

# region Utility


def overlapping(min_a: float, max_a: float, min_b: float, max_b: float) -> bool:
    return min_b < max_a and min_a < max_b


def rotate90(v: Vec2) -> Vec2:
    return Vec2(-v.y, v.x)


def rotate180(v: Vec2) -> Vec2:
    return Vec2(-v.x, -v.y)


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
        return Collision(rotate180(collision.penetration), collision.depth)
    
    return None


# endregion

# region Collision functions


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
    lc = circle.center - line.base
    projected = project_vector(lc, line.direction)
    nearest = line.base + projected

    return circle_point_collision(circle, nearest)


def circle_lineseg_collision(circle: Circle, line: LineSegment) -> bool:
    if circle_point_collision(circle, line.point1) or circle_point_collision(
        circle, line.point2
    ):
        return True

    line_distance = line.point2 - line.point1
    circle_distance = circle.center - line.point1
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


def rectangle_lineseg_collision(rectangle: Rectangle, segment: LineSegment) -> bool:
    line = Line(segment.point1, segment.point2 - segment.point1)
    if not rectangle_line_collision(rectangle, line):
        return False

    rect_min_x, rect_max_x = rectangle.origin.x, rectangle.origin.x + rectangle.size.x
    seg_min_x, seg_max_x = (
        min(segment.point1.x, segment.point2.x),
        max(segment.point1.x, segment.point2.x),
    )
    if not overlapping(rect_min_x, rect_max_x, seg_min_x, seg_max_x):
        return False

    rect_min_y, rect_max_y = rectangle.origin.y, rectangle.origin.y + rectangle.size.y
    seg_min_y, seg_max_y = (
        min(segment.point1.y, segment.point2.y),
        max(segment.point1.y, segment.point2.y),
    )
    return overlapping(rect_min_y, rect_max_y, seg_min_y, seg_max_y)


def separating_axis_for_rectangle(axis: LineSegment, rect: Rectangle) -> bool:
    n = axis.point1 - axis.point2

    rect_vertices = rect.vertices()
    rect_edge_a = LineSegment(next(rect_vertices), next(rect_vertices))
    rect_edge_b = LineSegment(next(rect_vertices), next(rect_vertices))
    a_min, a_max = project_segment(rect_edge_a, n)
    b_min, b_max = project_segment(rect_edge_b, n)
    a_min, a_max = min(a_min, a_max), max(a_min, a_max)
    b_min, b_max = min(b_min, b_max), max(b_min, b_max)

    p_min, p_max = min(a_min, b_min), max(a_max, b_max)
    axis_min, axis_max = project_segment(axis, n)

    return not overlapping(axis_min, axis_max, p_min, p_max)


def rectangle_oriented_rectangle_collision(
    rectangle: Rectangle, oriented_rectangle: OrientedRectangle
):
    if not rect_rect_collision(rectangle, oriented_rectangle.bounding_box):
        return False

    rect_vertices = [_ for _ in rectangle.vertices()]
    orect_vertices = [_ for _ in oriented_rectangle.vertices()]
    for axis in chain(oriented_rectangle.axes(), rectangle.axes()):
        a_min, a_max = min_max_vertex(axis, rect_vertices)
        b_min, b_max = min_max_vertex(axis, orect_vertices)
        if a_max < b_min or b_max < a_min:
            return False

    return True


def line_point_collision(line: Line, point: Vec2) -> bool:
    if point_point_collision(line.base, point):
        return True

    point_line = point - line.base
    return is_parallel_line(point_line, line.direction)


def line_segment_point_collision(line_segment: LineSegment, point: Vec2) -> bool:
    d = line_segment.point2 - line_segment.point1
    lp = point - line_segment.point1
    pr = project_vector(lp, d)

    return lp == pr and pr.mag <= d.mag and 0 <= pr.dot(d)


def oriented_rectangle_point_collision(
    oriented_rect: OrientedRectangle, point: Vec2
) -> bool:
    lr = Rectangle(Vec2(0, 0), oriented_rect.half_extent * 2)
    lp = (point - oriented_rect.center).rotate(
        -oriented_rect.rotation
    ) + oriented_rect.half_extent

    return rectangle_point_collision(lr, lp)


def line_line_segment_collision(line: Line, line_segment: LineSegment) -> bool:
    return not on_one_side(line, line_segment)


def line_oriented_rectangle_collision(
    line: Line, oriented_rectangle: OrientedRectangle
) -> bool:
    lr = Rectangle(Vec2(0, 0), oriented_rectangle.half_extent * 2)
    ll = Line(
        (line.base - oriented_rectangle.center).rotate(-oriented_rectangle.rotation)
        + oriented_rectangle.half_extent,
        line.direction.rotate(-oriented_rectangle.rotation),
    )

    return rectangle_line_collision(lr, ll)


def line_segment_oriented_rectangle_collision(
    line_segment: LineSegment, oriented_rectangle: OrientedRectangle
) -> bool:
    lr = Rectangle(Vec2(0, 0), oriented_rectangle.half_extent * 2)
    ls = LineSegment(
        (line_segment.point1 - oriented_rectangle.center).rotate(
            -oriented_rectangle.rotation
        )
        + oriented_rectangle.half_extent,
        (line_segment.point2 - oriented_rectangle.center).rotate(
            -oriented_rectangle.rotation
        )
        + oriented_rectangle.half_extent,
    )

    return rectangle_lineseg_collision(lr, ls)


def point_polygon_collision(point: Vec2, polygon: Polygon) -> bool:
    if not rectangle_point_collision(polygon.bounding_box, point):
        return False

    polygon_vertices = [_ for _ in polygon.vertices()]
    for axis in polygon.axes():
        point_min, point_max = min_max_vertex(axis, [point])
        poly_min, poly_max = min_max_vertex(axis, polygon_vertices)
        if point_max < poly_min or poly_max < point_min:
            return False

    return True


def rectangle_polygon_collision(rectangle: Rectangle, polygon: Polygon) -> bool:
    if not rect_rect_collision(rectangle, polygon.bounding_box):
        return False
    
    rect_vertices = [_ for _ in rectangle.vertices()]
    orect_vertices = [_ for _ in polygon.vertices()]
    for axis in chain(polygon.axes(), rectangle.axes()):
        a_min, a_max = min_max_vertex(axis, rect_vertices)
        b_min, b_max = min_max_vertex(axis, orect_vertices)
        if a_max < b_min or b_max < a_min:
            return False

    return True


# region Penetration functions


def circle_circle_penetration(c1: Circle, c2: Circle) -> Vec2 | None:
    distance = c1.center.distance(c2.center)
    radii = c1.radius + c2.radius

    if distance >= radii:
        return None

    penetration_depth = radii - distance
    penetration_vector = (c2.center - c1.center).from_magnitude(penetration_depth)

    return Collision(penetration_vector, penetration_depth)


def rectangle_rectangle_penetration(r1: Rectangle, r2: Rectangle) -> Vec2 | None:
    dx = (r1.origin.x + r1.size.x / 2) - (r2.origin.x + r2.size.x / 2)
    overlap_x = (r1.size.x / 2 + r2.size.x / 2) - abs(dx)

    dy = (r1.origin.y + r1.size.y / 2) - (r2.origin.y + r2.size.y / 2)
    overlap_y = (r1.size.y / 2 + r2.size.y / 2) - abs(dy)

    if overlap_x <= 0 or overlap_y <= 0:
        return None

    if overlap_x < overlap_y:
        penetration_depth = overlap_x
        penetration_vector = Vec2(
            penetration_depth if dx < 0 else -penetration_depth, 0
        )
    else:
        penetration_depth = overlap_y
        penetration_vector = Vec2(
            0, penetration_depth if dy < 0 else -penetration_depth
        )

    return Collision(penetration_vector, penetration_depth)

    # r1_left = r1.origin.x
    # r1_right = r1_left + r1.size.x
    # r2_left = r2.origin.x
    # r2_right = r2_left + r2.size.x

    # r1_bottom = r1.origin.y
    # r1_top = r1_bottom + r1.size.y
    # r2_bottom = r2.origin.y
    # r2_top = r2_bottom + r2.size.y

    # if not overlapping(r1_left, r1_right, r2_left, r2_right) and not overlapping(
    #     r1_bottom, r1_top, r2_bottom, r2_top
    # ):
    #     return None

    # x_overlap = min(r1_left, r1_right) - max(r1_left, r1_right)
    # y_overlap = min(r1_bottom, r2_bottom) - max(r1_top, r2_top)

    # if x_overlap < y_overlap:
    #     penetration_vector = Vec2(-x_overlap, 0) if r1.origin.x < r2.origin.x else Vec2(x_overlap, 0)
    #     penetration_depth = abs(x_overlap)
    # else:
    #     penetration_vector = Vec2(0, -y_overlap) if r1.origin.y < r2.origin.y else Vec2(0, y_overlap)
    #     penetration_depth = abs(y_overlap)

    # return Collision(penetration_vector, penetration_depth)


def overlap_on_axis(
    o1: OrientedRectangle, o2: OrientedRectangle, axis: Vec2
) -> float | None:
    proj1_min, proj1_max = project_vertices(o1.vertices(), axis)
    proj2_min, proj2_max = project_vertices(o2.vertices(), axis)
    overlap = min(proj1_max, proj2_max) - max(proj1_min, proj2_min)

    return overlap if overlap > 0 else None


def oriented_rectangle_oriented_rectangle_penetration(
    o1: OrientedRectangle, o2: OrientedRectangle
) -> Collision | None:
    min_penetration = inf
    penetration_axis = Vec2()

    for axis in chain(o1.axes(), o2.axes()):
        axis = axis.normalize()
        if overlap := overlap_on_axis(o1, o2, axis):
            if overlap < min_penetration:
                min_penetration = overlap
                penetration_axis = axis
        else:
            return None

    penetration_vector = penetration_axis.from_magnitude(min_penetration)

    return Collision(penetration_vector, min_penetration)


def circle_rectangle_penetration(c: Circle, r: Rectangle) -> Collision | None:
    closest_x = max(r.origin.x, min(c.center.x, r.origin.x + r.size.x))
    closest_y = max(r.origin.y, min(c.center.y, r.origin.y + r.size.y))
    closest_point = Vec2(closest_x, closest_y)

    center_to_closest = closest_point - c.center
    distance = center_to_closest.mag

    if distance >= c.radius:
        return None

    penetration_depth = c.radius - distance
    penetration_vector = center_to_closest.from_magnitude(penetration_depth)

    return Collision(penetration=penetration_vector, depth=penetration_depth)


def circle_oriented_rectangle_penetration(
    c: Circle, o: OrientedRectangle
) -> Collision | None:
    to_local = c.center - o.center
    cos_r, sin_r = cos(-o.rotation), sin(-o.rotation)
    local_center = Vec2(
        to_local.x * cos_r - to_local.y * sin_r, to_local.x * sin_r + to_local.y * cos_r
    )

    closest_x = max(-o.half_extent.x, min(local_center.x, o.half_extent.x))
    closest_y = max(-o.half_extent.y, min(local_center.y, o.half_extent.y))
    closest_point = Vec2(closest_x, closest_y)

    penetration_vector_local = local_center - closest_point
    penetration_distance = penetration_vector_local.mag

    if penetration_distance >= c.radius:
        return None

    penetration_depth = c.radius - penetration_distance
    penetration_vector_world = Vec2(
        penetration_vector_local.x * cos_r + penetration_vector_local.y * sin_r,
        -penetration_vector_local.x * sin_r + penetration_vector_local.y * cos_r,
    ).from_magnitude(penetration_depth)

    return Collision(penetration=penetration_vector_world, depth=penetration_depth)


def rectangle_oriented_rectangle_penetration(
    r: Rectangle, o: OrientedRectangle
) -> Collision | None:
    # Track the minimum penetration axis and depth
    min_penetration_depth = inf
    min_penetration_axis = Vec2()

    # SAT - Project both shapes onto each axis
    for axis in chain(r.axes(), o.axes()):
        # Project both shapes onto the axis
        rect_proj = [vertex.dot(axis) for vertex in r.vertices()]
        ortho_proj = [vertex.dot(axis) for vertex in o.vertices()]

        # Find min and max projections
        rect_min, rect_max = min(rect_proj), max(rect_proj)
        ortho_min, ortho_max = min(ortho_proj), max(ortho_proj)

        # Check for overlap
        overlap = min(rect_max, ortho_max) - max(rect_min, ortho_min)
        if overlap <= 0:
            return None  # No collision

        # Track the smallest penetration depth
        if overlap < min_penetration_depth:
            min_penetration_depth = overlap
            min_penetration_axis = axis if rect_min < ortho_min else -axis

    # Calculate the penetration vector
    penetration_vector = min_penetration_axis.from_magnitude(min_penetration_depth)

    # Return the Collision object with penetration vector and depth
    return Collision(penetration=penetration_vector, depth=min_penetration_depth)


# endregion

# region Minkowski difference functions

# endregion


# region Register class methods


@Line.collision.register
def _(self, line: Line) -> bool:
    return line_line_collision(self, line)


@Line.collision.register
def _(self, line_segment: LineSegment) -> bool:
    return line_line_segment_collision(self, line_segment)


@Line.collision.register
def _(self, circle: Circle) -> bool:
    return circle_line_collision(circle, self)


@Line.collision.register
def _(self, rectangle: Rectangle) -> bool:
    return rectangle_line_collision(rectangle, self)


@Line.collision.register
def _(self, oriented_rectangle: OrientedRectangle) -> bool:
    return line_oriented_rectangle_collision(self, oriented_rectangle)


@LineSegment.collision.register
def _(self, line: Line) -> bool:
    return line_line_segment_collision(line, self)


@LineSegment.collision.register
def _(self, line_segment: LineSegment) -> bool:
    return lineseg_lineseg_collision(self, line_segment)


@LineSegment.collision.register
def _(self, circle: Circle) -> bool:
    return circle_lineseg_collision(circle, self)


@LineSegment.collision.register
def _(self, rectangle: Rectangle) -> bool:
    return rectangle_line_collision(rectangle, self)


@LineSegment.collision.register
def _(self, oriented_rectangle: OrientedRectangle) -> bool:
    return line_segment_oriented_rectangle_collision(self, oriented_rectangle)


@Circle.collision.register
def _(self, line: Line) -> bool:
    return circle_line_collision(self, line)


@Circle.collision.register
def _(self, line_segment: LineSegment) -> bool:
    return circle_lineseg_collision(self, line_segment)


@Circle.collision.register
def _(self, circle: Circle) -> bool:
    return circle_circle_collision(self, circle)


@Circle.collision.register
def _(self, rectangle: Rectangle) -> bool:
    return circle_rectangle_collision(self, rectangle)


@Circle.collision.register
def _(self, oriented_rectangle: OrientedRectangle) -> bool:
    return circle_oriented_rectangle_collision(self, oriented_rectangle)


@Circle.penetration.register
def _(self, circle: Circle) -> Collision | None:
    return circle_circle_penetration(self, circle)


@Circle.penetration.register
def _(self, rectangle: Rectangle) -> Collision | None:
    return circle_rectangle_penetration(self, rectangle)


@Circle.penetration.register
def _(self, oriented_rectangle: OrientedRectangle) -> Collision | None:
    return circle_oriented_rectangle_penetration(self, oriented_rectangle)


@Rectangle.collision.register
def _(self, line: Line) -> bool:
    return rectangle_line_collision(self, line)


@Rectangle.collision.register
def _(self, line_segment: LineSegment) -> bool:
    return rectangle_lineseg_collision(self, line_segment)


@Rectangle.collision.register
def _(self, circle: Circle) -> bool:
    return circle_rectangle_collision(circle, self)


@Rectangle.collision.register
def _(self, rectangle: Rectangle) -> bool:
    return rect_rect_collision(self, rectangle)


@Rectangle.collision.register
def _(self, oriented_rectangle: OrientedRectangle) -> bool:
    return rectangle_oriented_rectangle_collision(self, oriented_rectangle)


@Rectangle.penetration.register
def _(self, rectangle: Rectangle) -> Vec2 | None:
    return rectangle_rectangle_penetration(self, rectangle)


@Rectangle.penetration.register
def _(self, circle: Circle) -> Collision | None:
    return reverse_collision(circle_rectangle_penetration(circle, self))


@Rectangle.penetration.register
def _(self, oriented_rectangle: OrientedRectangle) -> Collision | None:
    return rectangle_oriented_rectangle_penetration(self, oriented_rectangle)


@OrientedRectangle.collision.register
def _(self, line: Line) -> bool:
    return line_oriented_rectangle_collision(line, self)


@OrientedRectangle.collision.register
def _(self, line_segment: LineSegment) -> bool:
    return line_segment_oriented_rectangle_collision(line_segment, self)


@OrientedRectangle.collision.register
def _(self, circle: Circle) -> bool:
    return circle_oriented_rectangle_collision(circle, self)


@OrientedRectangle.collision.register
def _(self, rectangle: Rectangle) -> bool:
    return rectangle_oriented_rectangle_collision(rectangle, self)


@OrientedRectangle.collision.register
def _(self, oriented_rectangle: OrientedRectangle) -> bool:
    return oriented_rect_oriented_rect_collision(self, oriented_rectangle)


@OrientedRectangle.penetration.register
def _(self, oriented_rectangle: OrientedRectangle) -> Collision | None:
    return oriented_rectangle_oriented_rectangle_penetration(self, oriented_rectangle)


@OrientedRectangle.penetration.register
def _(self, rectangle: Rectangle) -> Vec2 | None:
    return reverse_collision(rectangle_oriented_rectangle_penetration(rectangle, self))


@OrientedRectangle.penetration.register
def _(self, circle: Circle) -> Collision | None:
    return reverse_collision(circle_rectangle_penetration(circle, self))


# endregion
