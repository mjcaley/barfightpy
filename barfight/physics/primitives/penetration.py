from itertools import chain
from math import cos, inf, sin

from pyglet.math import Vec2

from ... import pyglet_ext as _
from .objects import Circle, Collision, OrientedRectangle, Polygon, Rectangle
from .utility import project_vertices, reverse_collision


def circle_circle_penetration(c1: Circle, c2: Circle) -> Vec2 | None:
    distance = c1.center.distance(c2.center)
    radii = c1.radius + c2.radius

    if distance >= radii:
        return None

    penetration_depth = radii - distance
    penetration_vector = (c2.center - c1.center).normalize() * penetration_depth

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

    penetration_vector = penetration_axis.normalize() * min_penetration

    return Collision(penetration_vector, min_penetration)


def circle_rectangle_penetration(c: Circle, r: Rectangle) -> Collision | None:
    closest_x = max(r.origin.x, min(c.center.x, r.origin.x + r.size.x))
    closest_y = max(r.origin.y, min(c.center.y, r.origin.y + r.size.y))
    closest_point = Vec2(closest_x, closest_y)

    center_to_closest = closest_point - c.center
    distance = center_to_closest.length()

    if distance >= c.radius:
        return None

    penetration_depth = c.radius - distance
    penetration_vector = center_to_closest.normalize() * penetration_depth

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
    penetration_distance = penetration_vector_local.length()

    if penetration_distance >= c.radius:
        return None

    penetration_depth = c.radius - penetration_distance
    penetration_vector_world = (
        Vec2(
            penetration_vector_local.x * cos_r + penetration_vector_local.y * sin_r,
            -penetration_vector_local.x * sin_r + penetration_vector_local.y * cos_r,
        ).normalize()
        * penetration_depth
    )

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
    penetration_vector = min_penetration_axis.normalize() * min_penetration_depth

    # Return the Collision object with penetration vector and depth
    return Collision(penetration=penetration_vector, depth=min_penetration_depth)


def polygon_polygon_penetration(p1: Polygon, p2: Polygon) -> Collision | None:
    min_penetration = inf
    penetration_axis = Vec2()

    for axis in chain(p1.axes(), p2.axes()):
        axis = axis.normalize()
        p1_min, p1_max = project_vertices(p1.vertices(), axis)
        p2_min, p2_max = project_vertices(p2.vertices(), axis)
        overlap = min(p1_max, p2_max) - max(p1_min, p2_min)

        if overlap <= 0:
            return None

        if overlap < min_penetration:
            min_penetration = overlap
            penetration_axis = axis

    penetration_vector = penetration_axis.normalize() * min_penetration

    return Collision(penetration_vector, min_penetration)


def polygon_circle_penetration(polygon: Polygon, circle: Circle) -> Collision | None:
    min_penetration = inf
    penetration_axis = Vec2()

    for axis in polygon.axes():
        axis = axis.normalize()
        p_min, p_max = project_vertices(polygon.vertices(), axis)
        c_min, c_max = project_vertices(
            [
                circle.center + axis.normalize().normalize() * circle.radius,
                circle.center + axis.normalize().normalize() * -circle.radius,
            ],
            axis,
        )
        overlap = min(p_max, c_max) - max(p_min, c_min)

        if overlap <= 0:
            return None

        if overlap < min_penetration:
            min_penetration = overlap
            penetration_axis = axis

    penetration_vector = penetration_axis.normalize() * min_penetration

    return Collision(penetration_vector, min_penetration)


def polygon_rectangle_penetration(
    polygon: Polygon, rectangle: Rectangle
) -> Collision | None:
    min_penetration = inf
    penetration_axis = Vec2()

    for axis in chain(polygon.axes(), rectangle.axes()):
        axis = axis.normalize()
        p_min, p_max = project_vertices(polygon.vertices(), axis)
        r_min, r_max = project_vertices(rectangle.vertices(), axis)
        overlap = min(p_max, r_max) - max(p_min, r_min)

        if overlap <= 0:
            return None

        if overlap < min_penetration:
            min_penetration = overlap
            penetration_axis = axis

    penetration_vector = penetration_axis.normalize() * min_penetration

    return Collision(penetration_vector, min_penetration)


def polygon_oriented_rectangle_penetration(
    polygon: Polygon, oriented_rectangle: OrientedRectangle
) -> Collision | None:
    min_penetration = inf
    penetration_axis = Vec2()

    for axis in chain(polygon.axes(), oriented_rectangle.axes()):
        axis = axis.normalize()
        p_min, p_max = project_vertices(polygon.vertices(), axis)
        o_min, o_max = project_vertices(oriented_rectangle.vertices(), axis)
        overlap = min(p_max, o_max) - max(p_min, o_max)

        if overlap <= 0:
            return None

        if overlap < min_penetration:
            min_penetration = overlap
            penetration_axis = axis

    penetration_vector = penetration_axis.normalize() * min_penetration

    return Collision(penetration_vector, min_penetration)


def polygon_point_penetration(polygon: Polygon, point: Vec2) -> Collision | None:
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

    penetration_vector = penetration_axis.normalize() * min_penetration
    return Collision(penetration_vector, min_penetration)


@Circle.penetration.register
def _(self, circle: Circle) -> Collision | None:  # noqa: F811
    return circle_circle_penetration(self, circle)


@Circle.penetration.register
def _(self, rectangle: Rectangle) -> Collision | None:
    return circle_rectangle_penetration(self, rectangle)


@Circle.penetration.register
def _(self, oriented_rectangle: OrientedRectangle) -> Collision | None:
    return circle_oriented_rectangle_penetration(self, oriented_rectangle)


@Circle.penetration.register
def _(self, polygon: Polygon) -> Collision | None:
    return reverse_collision(polygon_circle_penetration(polygon, self))


@Rectangle.penetration.register
def _(self, rectangle: Rectangle) -> Vec2 | None:
    return rectangle_rectangle_penetration(self, rectangle)


@Rectangle.penetration.register
def _(self, circle: Circle) -> Collision | None:
    return reverse_collision(circle_rectangle_penetration(circle, self))


@Rectangle.penetration.register
def _(self, oriented_rectangle: OrientedRectangle) -> Collision | None:
    return rectangle_oriented_rectangle_penetration(self, oriented_rectangle)


@Rectangle.penetration.register
def _(self, polygon: Polygon) -> Collision | None:
    return reverse_collision(polygon_rectangle_penetration(polygon, self))


@OrientedRectangle.penetration.register
def _(self, oriented_rectangle: OrientedRectangle) -> Collision | None:
    return oriented_rectangle_oriented_rectangle_penetration(self, oriented_rectangle)


@OrientedRectangle.penetration.register
def _(self, rectangle: Rectangle) -> Vec2 | None:
    return reverse_collision(rectangle_oriented_rectangle_penetration(rectangle, self))


@OrientedRectangle.penetration.register
def _(self, circle: Circle) -> Collision | None:
    return reverse_collision(circle_rectangle_penetration(circle, self))


@OrientedRectangle.penetration.register
def _(self, polygon: Polygon) -> Collision | None:
    return reverse_collision(polygon_oriented_rectangle_penetration(polygon, self))


@Polygon.penetration.register
def _(self, polygon: Polygon) -> Collision | None:
    return polygon_polygon_penetration(self, polygon)


@Polygon.penetration.register
def _(self, circle: Circle) -> Collision | None:
    return polygon_circle_penetration(self, circle)


@Polygon.penetration.register
def _(self, rectangle: Rectangle) -> Collision | None:
    return polygon_rectangle_penetration(self, rectangle)


@Polygon.penetration.register
def _(self, oriented_rectangle: OrientedRectangle) -> Collision | None:
    return polygon_oriented_rectangle_penetration(self, oriented_rectangle)


@Polygon.penetration.register
def _(self, point: Vec2) -> Collision | None:
    return polygon_point_penetration(self, point)
