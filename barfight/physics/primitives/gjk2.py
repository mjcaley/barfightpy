"""Implementation based off https://observablehq.com/@esperanc/2d-gjk-and-epa-algorithms"""

from dataclasses import dataclass
from math import inf
from typing import Protocol

from pyglet.math import Vec2


class GJKShape(Protocol):
    def furthest(self, direction: Vec2) -> Vec2: ...

    @property
    def center(self) -> Vec2: ...


def triple_product(a: Vec2, b: Vec2, c: Vec2) -> Vec2:
    z = a.x * b.y - a.y * b.x

    return Vec2(-c.y * z, c.x * z)


def support(points: list[Vec2], direction: Vec2) -> Vec2:
    max_dot = -inf
    best: Vec2
    for point in points:
        dot = point.dot(direction)
        if dot > max_dot:
            max_dot = dot
            best = point

    return best


def same_direction(a: Vec2, b: Vec2) -> bool:
    """Check if vectors point in roughly the same direction"""
    return a.dot(b) > 0


def support2(shape1: GJKShape, shape2: GJKShape, direction: Vec2) -> Vec2:
    return shape1.furthest(direction) - shape2.furthest(-direction)


def perpendicular(v: Vec2) -> Vec2:
    return Vec2(-v.y, v.x)


def left(v: Vec2) -> Vec2:
    return Vec2(v.y, -v.x)


GJK_EPSILON = 0.00001


def gjk_orig(shape1: GJKShape, shape2: GJKShape) -> list[Vec2] | None:
    # First point
    v = (shape2.center - shape1.center).normalize()
    if v == Vec2(0, 0):
        v = Vec2(1, 0)
    a = support2(shape1, shape2, v)
    
    # Is a past the origin?
    if a.dot(v) <= 0.0:
        return None

    # First direction
    v = -a

    # Second point
    b = support2(shape1, shape2, v)

    # Second direction
    ab = b - a
    v = triple_product(ab, -a, ab)
    if v.length_squared() <= GJK_EPSILON:
        v = left(ab)

    while True:
        # Third point
        c = support2(shape1, shape2, v)
        if c.dot(v) <= 0.0:
            # Not past the origin
            return None

        c0 = -c
        cb = b - c
        ca = a - c

        cb_perp = triple_product(ca, cb, cb)
        ca_perp = triple_product(cb, ca, ca)

        if ca_perp.dot(c0) > 0.0:
            b = c
            v = ca_perp
        elif cb_perp.dot(c0) > 0.0:
            a = c
            v = cb_perp
        else:
            return [a, b, c]


GJK_MAX_ITERATIONS = 32
# DETECT_EPSILON = 0.000001
DETECT_EPSILON = 0.5
while 1.0 + DETECT_EPSILON > 1.0:
    DETECT_EPSILON *= 0.5


def gjk(shape1: GJKShape, shape2: GJKShape) -> list[Vec2] | None:
    simplex = []
    d = (shape1.center - shape2.center).normalize()
    if d == Vec2(0, 0):
        d = Vec2(1, 0)
    simplex.append(support2(shape1, shape2, d))

    # Past the origin?
    if simplex[-1].dot(d) <= 0.0:
        return None
    
    d = -d

    for _ in range(GJK_MAX_ITERATIONS):
        support_point = support2(shape1, shape2, d)
        simplex.append(support_point)

        # Past the origin?
        if support_point.dot(d) <= DETECT_EPSILON:
            return None
        else:
            # Check simplex
            a = simplex[-1]
            ao = -a
            if len(simplex) == 3:
                b = simplex[1]
                c = simplex[0]

                ab = b - a
                ac = c - a

                dot = ab.x * ac.y - ac.x * ab.y
                ac_perp = Vec2(-ac.y * dot, ac.x * dot)

                ac_location = ac_perp.dot(ao)
                if ac_location >= 0.0:
                    simplex.pop(1)
                    d = ac_perp
                else:
                    ab_perp = Vec2(ab.y * dot, -ab.x * dot)
                    ab_location = ab_perp.dot(ao)
                    if ab_location < 0.0:
                        return simplex
                    else:
                        simplex.pop(0)
                        d = ab_perp
            else:
                b = simplex[0]
                ab = b - a
                d = triple_product(ab, ao, ab)
                if d.length_squared() <= GJK_EPSILON:
                    d = left(ab)

    return None


@dataclass
class Edge:
    distance: float
    index: int
    first: Vec2
    second: Vec2
    normal: Vec2


def closest_edge(polytope: list[Vec2]) -> Edge:
    npts = len(polytope)
    dmin = inf
    closest: Edge
    for i in range(npts):
        p, q = polytope[i], polytope[(i + 1) % npts]
        e = q - p
        n = triple_product(e, p, e).normalize()
        dist = n.dot(p)
        if dist < dmin:
            dmin = dist
            closest = Edge(dist, i, p, q, n)

    return closest


@dataclass
class Intersection:
    first: Vec2
    second: Vec2
    distance: float
    normal: Vec2


def epa(shape1: GJKShape, shape2: GJKShape, a: Vec2, b: Vec2, c: Vec2):
    polytope = [a, b, c]

    while True:
        edge = closest_edge(polytope)
        r = support2(shape1, shape2, edge.normal)
        if abs(edge.normal.dot(r) - edge.distance < 0.0001):
            return Intersection(edge.first, edge.second, edge.distance, edge.normal)
        polytope.insert(edge.index + 1, r)
