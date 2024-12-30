from math import cos, pi, sin

from pyglet.math import Vec2

from .objects import Circle, OrientedRectangle, Polygon, Rectangle


def minkowski_difference_circles(c1: Circle, c2: Circle) -> Circle:
    """Calculate the Minkowski difference between two circles."""
    diff_center = c1.center - c2.center
    sum_radius = c1.radius + c2.radius

    return Circle(diff_center, sum_radius)


def minkowski_difference_rectangles(r1: Rectangle, r2: Rectangle) -> Polygon:
    """Calculate the Minkowski difference between two rectangles."""
    vertices = []
    for vertex_a in r1.vertices():
        for vertex_b in r2.vertices():
            vertices.append(vertex_a - vertex_b)

    return Polygon(vertices)


def minkowski_difference_oriented_rectangles(
    o1: OrientedRectangle, o2: OrientedRectangle
) -> Polygon:
    """Calculate the Minkowski difference between two oriented rectangles."""
    vertices = []
    for vertex_a in o1.vertices():
        for vertex_b in o2.vertices():
            vertices.append(vertex_a - vertex_b)

    return Polygon(vertices)


def minkowski_difference_circle_rectangle(circle: Circle, rect: Rectangle) -> Polygon:
    """Calculate the Minkowski difference between a circle and a rectangle."""
    vertices = []
    num_points = 8  # Approximation points for circle
    for i in range(num_points):
        angle = 2 * pi * i / num_points
        circle_point = circle.center + Vec2(cos(angle), sin(angle)) * circle.radius
        for rect_vertex in rect.vertices():
            vertices.append(circle_point - rect_vertex)

    return Polygon(vertices)


def minkowski_difference_circle_oriented_rectangle(
    circle: Circle, rect: OrientedRectangle
) -> Polygon:
    """Calculate the Minkowski difference between a circle and an oriented rectangle."""
    vertices = []
    num_points = 8  # Approximation points for circle
    for i in range(num_points):
        angle = 2 * pi * i / num_points
        circle_point = circle.center + Vec2(cos(angle), sin(angle)) * circle.radius
        for rect_vertex in rect.vertices():
            vertices.append(circle_point - rect_vertex)

    return Polygon(vertices)


def minkowski_difference_circle_polygon(c: Circle, p: Polygon) -> Polygon:
    """Calculate Circle-Polygon Minkowski difference."""
    vertices = []
    num_points = 8  # Approximation points for circle
    for i in range(num_points):
        angle = 2 * pi * i / num_points
        circle_point = c.center + Vec2(cos(angle), sin(angle)) * c.radius
        for poly_vertex in p.vertices():
            vertices.append(circle_point - poly_vertex)

    return Polygon(vertices)


def minkowski_difference_polygon_polygon(p1: Polygon, p2: Polygon) -> Polygon:
    """Calculate the Minkowski difference between two polygons."""
    vertices = []
    for vertex_a in p1.vertices():
        for vertex_b in p2.vertices():
            vertices.append(vertex_a - vertex_b)

    return Polygon(vertices)


def minkowski_difference_polygon_rectangle(poly: Polygon, rect: Rectangle) -> Polygon:
    """Calculate the Minkowski difference between a polygon and a rectangle."""
    vertices = []
    for vertex_a in poly.vertices():
        for vertex_b in rect.vertices():
            vertices.append(vertex_a - vertex_b)

    return Polygon(vertices)


def minkowski_difference_polygon_oriented_rectangle(
    poly: Polygon, rect: OrientedRectangle
) -> Polygon:
    """Calculate the Minkowski difference between a polygon and an oriented rectangle."""
    vertices = []
    for vertex_a in poly.vertices():
        for vertex_b in rect.vertices():
            vertices.append(vertex_a - vertex_b)

    return Polygon(vertices)


@Circle.minkowski.register
def _(self, c: Circle) -> Circle:
    return minkowski_difference_circles(self, c)


@Circle.minkowski.register
def _(self, r: Rectangle) -> Polygon:
    return minkowski_difference_circle_rectangle(self, r)


@Circle.minkowski.register
def _(self, o: OrientedRectangle) -> Polygon:
    return minkowski_difference_circle_oriented_rectangle(self, o)


@Circle.minkowski.register
def _(self, p: Polygon) -> Polygon:
    return minkowski_difference_circle_polygon(self, p)


@Rectangle.minkowski.register
def _(self, r: Rectangle) -> Polygon:
    return minkowski_difference_rectangles(self, r)


@Rectangle.minkowski.register
def _(self, c: Circle) -> Polygon:
    return minkowski_difference_circle_rectangle(c, self)


@Rectangle.minkowski.register
def _(self, o: OrientedRectangle) -> Polygon:
    lo = OrientedRectangle(self.origin + (self.size / 2), self.size / 2)

    return minkowski_difference_oriented_rectangles(lo, o)


@Rectangle.minkowski.register
def _(self, p: Polygon) -> Polygon:
    return minkowski_difference_polygon_rectangle(p, self)


@OrientedRectangle.minkowski.register
def _(self, o: OrientedRectangle) -> Polygon:
    return minkowski_difference_oriented_rectangles(self, o)


@OrientedRectangle.minkowski.register
def _(self, c: Circle) -> Polygon:
    return minkowski_difference_circle_oriented_rectangle(c, self)


@OrientedRectangle.minkowski.register
def _(self, r: Rectangle) -> Polygon:
    lo = OrientedRectangle(r.origin + (r.size / 2), r.size / 2)

    return minkowski_difference_oriented_rectangles(self, lo)


@OrientedRectangle.minkowski.register
def _(self, p: Polygon) -> Polygon:
    return minkowski_difference_polygon_oriented_rectangle(p, self)


@Polygon.minkowski.register
def _(self, c: Circle) -> Polygon:
    return minkowski_difference_circle_polygon(c, self)


@Polygon.minkowski.register
def _(self, r: Rectangle) -> Polygon:
    return minkowski_difference_polygon_rectangle(self, r)


@Polygon.minkowski.register
def _(self, o: OrientedRectangle) -> Polygon:
    return minkowski_difference_polygon_oriented_rectangle(self, o)


@Polygon.minkowski.register
def _(self, p: Polygon) -> Polygon:
    return minkowski_difference_polygon_polygon(self, p)
