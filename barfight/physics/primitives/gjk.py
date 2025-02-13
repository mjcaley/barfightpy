from enum import Enum, auto
from typing import Protocol

from pyglet.math import Vec2, Vec3


class GJKShape(Protocol):
    def furthest(self, direction: Vec2) -> Vec2: ...

    @property
    def center(self) -> Vec2: ...


def support(shape1: GJKShape, shape2: GJKShape, direction: Vec2) -> Vec2:
    furthest1 = shape1.furthest(direction)
    furthest2 = shape2.furthest(-direction)

    return furthest1 - furthest2


def triple_product(v1: Vec2, v2: Vec2, v3: Vec2) -> Vec2:
    a = Vec3(v1.x, v2.y, 0)
    b = Vec3(v2.x, v2.y, 0)
    c = Vec3(v3.x, v3.y, 0)

    first = a.cross(b)
    second = first.cross(c)

    return Vec2(second.x, second.y)


class SimplexState(Enum):
    Evolving = auto()
    NoIntesection = auto()
    Intersection = auto()


class Simplex:
    def __init__(self, shape1: GJKShape, shape2: GJKShape):
        self.shape1 = shape1
        self.shape2 = shape2
        self._points: list[Vec2] = []
        self.search_direction = Vec2()
        self.finished = False
        self.colliding = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(shape1={repr(self.shape1)}, shape2={repr(self.shape2)})"

    def __str__(self) -> str:
        return f"Simplex - Points: {self._points}, Direction: {self.search_direction}, Colliding: {self.colliding}, Finished: {self.finished}"

    def support(self) -> Vec2:
        furthest1 = self.shape1.furthest(self.search_direction)
        furthest2 = self.shape2.furthest(-self.search_direction)

        return furthest1 - furthest2

    def add_support(self) -> bool:
        new_vertex = self.shape1.furthest(self.search_direction) - self.shape2.furthest(
            -self.search_direction
        )
        self._points.append(new_vertex)

        return self.search_direction.dot(new_vertex) >= 0

    def gjk(self) -> bool:
        while True:
            match self.evolve():
                case SimplexState.Evolving:
                    continue
                case _:
                    return self.colliding

    def evolve(self):
        match len(self._points):
            case 0:
                self.search_direction = self.shape2.center - self.shape1.center
            case 1:
                self.search_direction = -self.search_direction
            case 2:
                a, b = self._points
                ab = b - a  # Line from the first two vertices
                a0 = -a  # Line from the first vertex to the origin

                # Get direction perpendicular to cb, towards the origin
                self.search_direction = triple_product(ab, a0, ab)
            case 3:
                # Check if simplex containx the origin
                c, b, a = self._points

                c0 = -c  # Latest point to the origin
                bc = b - c
                ca = a - c

                bc_normal = triple_product(ca, bc, bc)
                ca_normal = triple_product(bc, ca, ca)

                if bc_normal.dot(c0) > 0:
                    # origin is outside the line bc
                    # remove point A and add a new support point in the direction of bc_normal
                    self._points.remove(a)
                    self.search_direction = bc_normal
                elif ca_normal.dot(c0) > 0:
                    # the origin is outside line ca
                    # remove point B and add a new support point in the direction of ca_normal
                    self._points.remove(b)
                    self.search_direction = ca_normal
                else:
                    self.finished = self.colliding = True
                    return SimplexState.Intersection
            case _:
                self.finished = True
                raise ValueError("Simplex is in bad state")

        if self.add_support():
            return SimplexState.Evolving
        else:
            self.finished = True
            return SimplexState.NoIntesection
