"""Implementation based off https://observablehq.com/@esperanc/2d-gjk-and-epa-algorithms"""

from dataclasses import dataclass
from enum import Enum, auto
from heapq import heappop, heappush
from itertools import chain, islice, pairwise
from math import inf, sqrt
from typing import Protocol, Self

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


def right(v: Vec2) -> Vec2:
    return Vec2(-v.y, v.x)


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


class WindingDirection(Enum):
    CW = -1
    CCW = 1


class Edge:
    def __init__(self, point1: Vec2, point2: Vec2, winding: WindingDirection):
        self.point1 = point1
        self.point2 = point2
        
        normal = point2 - point1
        if winding == WindingDirection.CW:
            self.normal = right(normal).normalize()
        else:
            self.normal = left(normal).normalize()

        self.distance = abs(self.point1.x * self.normal.x + self.point1.y * self.normal.y)
        
    def __gt__(self, other: Self) -> bool:
        return self.distance > other.distance
        # if self.distance < other.distance:
        #     return -1
        # elif self.distance > other.distance:
        #     return 1
        # else:
        #     return 0


def get_winding(simplex: list[Vec2]) -> WindingDirection:
    for a, b in pairwise(chain(simplex, islice(simplex, 1))):
        if a.cross(b) > 0:
            return WindingDirection.CCW
        elif a.cross(b) < 0:
            return WindingDirection.CW


class EPASimplex:
    def __init__(self, simplex: list[Vec2]):
        self.simplex = simplex
        self.winding = get_winding(self.simplex)
        self.queue = []
        for a, b in pairwise(chain(simplex, islice(simplex, 1))):
            heappush(self.queue, Edge(a, b, self.winding))

    def closest_edge(self) -> Edge:
        return self.queue[0]
    
    def expand(self, point: Vec2):
        edge: Edge = heappop(self.queue)
        edge1 = Edge(edge.point1, point, self.winding)
        edge2 = Edge(point, edge.point2, self.winding)
        heappush(self.queue, edge1)
        heappush(self.queue, edge2)


@dataclass(frozen=True)
class Penetration:
    normal: Vec2
    depth: float


EPA_MAX_ITERATIONS = 100
EPA_EPSILON = sqrt(GJK_EPSILON)


def epa(shape1: GJKShape, shape2: GJKShape, a: Vec2, b: Vec2, c: Vec2):
    epa_simplex = EPASimplex([a, b, c])

    for _ in range(EPA_MAX_ITERATIONS):
        edge = epa_simplex.closest_edge()
        support_point = support2(shape1, shape2, edge.normal)

        projection = support_point.dot(edge.normal)
        if projection - edge.distance < EPA_EPSILON:
            return Penetration(edge.normal, projection)
        
        epa_simplex.expand(support_point)

    return Penetration(edge.normal, support_point.dot(edge.normal))
