"""Implementation based off https://observablehq.com/@esperanc/2d-gjk-and-epa-algorithms"""

from dataclasses import dataclass
from math import inf

from pyglet.math import Vec2


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


def support2(points1: list[Vec2], points2: list[Vec2], direction: Vec2) -> Vec2:
    return support(points1, direction) - support(points2, -direction)


def gjk(points1: list[Vec2], points2: list[Vec2]) -> list[Vec2] | None:
    # First point
    a = support2(points1, points2, Vec2(1, 1))

    # First direction
    v = -a

    # Second point
    b = support2(points1, points2, v)

    # Second direction
    ab = b - a
    v = triple_product(ab, -a, ab)

    while True:
        # Third point
        c = support2(points1, points2, v)
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


def epa(points1: list[Vec2], points2: list[Vec2], a: Vec2, b: Vec2, c: Vec2):
    polytope = [a, b, c]

    while True:
        edge = closest_edge(polytope)
        r = support2(points1, points2, edge.normal)
        if abs(edge.normal.dot(r) - edge.distance < 0.0001):
            return Intersection(edge.first, edge.second, edge.distance, edge.normal)
        polytope.insert(edge.index + 1, r)
