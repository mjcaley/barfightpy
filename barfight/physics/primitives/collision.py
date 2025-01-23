from itertools import chain

from pyglet.math import Vec2

from ... import pyglet_ext as _
from .objects import (
    Circle,
    Line,
    LineSegment,
    OrientedRectangle,
    Point,
    Polygon,
    Rectangle,
)
from .utility import (
    clamp_rectangle,
    equivalent_lines,
    is_parallel_line,
    min_max_vertex,
    on_one_side,
    overlapping,
    project_segment,
    project_vector,
)


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


def circle_point_collision(circle: Circle, point: Point) -> bool:
    return circle.center.distance(point.point) <= circle.radius


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


def rectangle_point_collision(rectangle: Rectangle, point: Point) -> bool:
    left = rectangle.origin.x
    right = left + rectangle.size.x
    bottom = rectangle.origin.y
    top = bottom + rectangle.size.y

    return (
        left <= point.point.x
        and bottom <= point.point.y
        and point.point.x <= right
        and point.point.y <= top
    )


def rectangle_line_collision(rectangle: Rectangle, line: Line) -> bool:
    n = line.direction.rotate90()

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


def line_point_collision(line: Line, point: Point) -> bool:
    if line.base == point.point:
        return True

    point_line = point - line.base
    return is_parallel_line(point_line, line.direction)


def line_segment_point_collision(line_segment: LineSegment, point: Point) -> bool:
    d = line_segment.point2 - line_segment.point1
    lp = point.point - line_segment.point1
    pr = project_vector(lp, d)

    return lp == pr and pr.mag <= d.mag and 0 <= pr.dot(d)


def oriented_rectangle_point_collision(
    oriented_rect: OrientedRectangle, point: Point
) -> bool:
    lr = Rectangle(Vec2(0, 0), oriented_rect.half_extent * 2)
    lp = (point.point - oriented_rect.center).rotate(
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


def point_polygon_collision(point: Point, polygon: Polygon) -> bool:
    if not rectangle_point_collision(polygon.bounding_box, point.point):
        return False

    polygon_vertices = [_ for _ in polygon.vertices()]
    for axis in polygon.axes():
        point_min, point_max = min_max_vertex(axis, [point.point])
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


def circle_polygon_collision(circle: Circle, polygon: Polygon) -> bool:
    for axis in polygon.axes():
        p_min, p_max = min_max_vertex(axis, polygon.vertices())
        c_min, c_max = min_max_vertex(
            axis,
            [
                circle.center + axis.normalize().from_magnitude(circle.radius),
                circle.center + axis.normalize().from_magnitude(-circle.radius),
            ],
        )
        if p_max < c_min or c_max < p_min:
            return False

    return True


def oriented_rectangle_polygon_collision(
    oriented_rectangle: OrientedRectangle, polygon: Polygon
) -> bool:
    for axis in chain(oriented_rectangle.axes(), polygon.axes()):
        p_min, p_max = min_max_vertex(axis, polygon.vertices())
        o_min, o_max = min_max_vertex(axis, oriented_rectangle.vertices())
        if p_max < o_min or o_max < p_min:
            return False

    return True


def polygon_polygon_collision(p1: Polygon, p2: Polygon) -> bool:
    for axis in chain(p1.axes(), p2.axes()):
        p1_min, p1_max = min_max_vertex(axis, p1.vertices())
        p2_min, p2_max = min_max_vertex(axis, p2.vertices())
        if p1_max < p2_min or p2_max < p1_min:
            return False

    return True


def polygon_point_collision(polygon: Polygon, point: Point) -> bool:
    min_penetration = inf
    penetration_axis = Vec2()

    for axis in polygon.axes():
        axis = axis.normalize()
        p_min, p_max = project_vertices(polygon.vertices(), axis)
        point_proj = point.dot(axis)

        if point_proj < p_min:
            overlap = p_min - point_proj
        elif point_proj > p_max:
            overlap = point_proj - p_max
        else:
            # Point is between min/max - use smallest distance to either boundary
            overlap = min(point_proj - p_min, p_max - point_proj)

        if overlap < min_penetration:
            min_penetration = overlap
            penetration_axis = axis

    if min_penetration == inf:
        return None

    penetration_vector = penetration_axis.from_magnitude(min_penetration)
    return Collision(penetration_vector, min_penetration)


@Point.collision.register
def _(self, point: Point) -> bool:  # noqa: F811
    return self.point == point.point


@Point.collision.register
def _(self, line: Line) -> bool:
    return line_point_collision(line, self)


@Point.collision.register
def _(self, line_segment: LineSegment) -> bool:
    return line_segment_point_collision(line_segment, self)


@Point.collision.register
def _(self, circle: Circle) -> bool:
    return circle_point_collision(circle, self)


@Point.collision.register
def _(self, rect: Rectangle) -> bool:
    return rectangle_point_collision(rect, self)


@Point.collision.register
def _(self, rect: OrientedRectangle) -> bool:
    return oriented_rectangle_point_collision(rect, self)


@Line.collision.register
def _(self, point: Point) -> bool:
    return line_point_collision(self, point.point)


@Line.collision.register
def _(self, polygon: Polygon) -> bool:
    return  # TODO: Implement function


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
def _(self, point: Point) -> bool:
    return line_segment_point_collision(self, point)


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
def _(self, point: Point) -> bool:
    return circle_point_collision(self, point)


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


@Circle.collision.register
def _(self, polygon: Polygon) -> bool:
    return circle_polygon_collision(self, polygon)


@Rectangle.collision.register
def _(self, point: Point) -> bool:
    return rectangle_point_collision(self, point)


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


@Rectangle.collision.register
def _(self, polygon: Polygon) -> bool:
    return rectangle_polygon_collision(self, polygon)


@OrientedRectangle.collision.register
def _(self, point: Point) -> bool:
    return oriented_rectangle_point_collision(self, point)


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


@OrientedRectangle.collision.register
def _(self, polygon: Polygon) -> bool:
    return oriented_rectangle_polygon_collision(self, polygon)


@Polygon.collision.register
def _(self, polygon: Polygon) -> bool:
    return polygon_polygon_collision(self, polygon)


@Polygon.collision.register
def _(self, point: Point) -> bool:
    return point_polygon_collision(point, self)


@Polygon.collision.register
def _(self, circle: Circle) -> bool:
    return circle_polygon_collision(circle, self)


@Polygon.collision.register
def _(self, rectangle: Rectangle) -> bool:
    return rectangle_polygon_collision(rectangle, self)


@Polygon.collision.register
def _(self, oriented_rectangle: OrientedRectangle) -> bool:
    return oriented_rectangle_polygon_collision(oriented_rectangle, self)
