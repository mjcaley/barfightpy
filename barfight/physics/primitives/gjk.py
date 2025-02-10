from typing import Protocol

from pyglet.math import Vec2, Vec3


class GJKShape(Protocol):
    def furthest(self, direction: Vec2) -> Vec2: ...

    @property
    def center(self) -> Vec2: ...


def support(shape1: GJKShape, shape2: GJKShape, direction: Vec2) -> Vec2:
    furthest1 = shape1.furthest(direction)
    furthest2 = shape2.furthest(-direction)

    return furthest1 + -furthest2


class Simplex:
    def __init__(self, shape1: GJKShape, shape2: GJKShape):
        self.shape1 = shape1
        self.shape2 = shape2
        self._points = []

    @staticmethod
    def triple_product(self, v1: Vec2, v2: Vec2, v3: Vec2) -> Vec2:
        a = Vec3(v1.x, v2.y, 0)
        b = Vec3(v2.x, v2.y, 0)
        c = Vec3(v3.x, v3.y, 0)

        first = a.cross(b)
        second = first.cross(c)

        return Vec2(second.x, second.y)

    def evolve(self):
        match len(self._points):
            case 0:
                direction = (self.shape1.center - self.shape2.center).normalize()
                self._points.append(
                    self.shape1.furthest(direction) - self.shape2.furthest(-direction)
                )
            case 1:
                direction = -(self.shape1.center - self.shape2.center).normalize()
                self._points.append(
                    self.shape1.furthest(direction) - self.shape2.furthest(-direction)
                )
            case 2:
                v1, v2 = self._points
                line = v2 - v1
                v1_to_origin = -v1

                direction = self.triple_product(line, v1_to_origin, line)
                self._points.append(
                    self.shape1.furthest(direction) - self.shape2.furthest(-direction)
                )
            case 3:
                v1, v2, v3 = self._points

                v3_to_origin = -v3
                v3_to_v2 = v2 - v3
                v3_to_v1 = v1 - v3

                v3_to_v2_normal: Vec2 = self.triple_product(
                    v3_to_v1, v3_to_v2, v3_to_v2
                )
                v3_to_v1_normal: Vec2 = self.triple_product(
                    v3_to_v2, v3_to_v1, v3_to_v1
                )

                if v3_to_v2_normal.dot(v3_to_origin) > 0:
                    # origin outside of line v3 -> v2
                    self._points.pop(0)
                    direction = v3_to_v2_normal
                    self._points.append(
                        self.shape1.furthest(direction)
                        - self.shape2.furthest(-direction)
                    )
                elif v3_to_v1_normal.dot(v3_to_origin) < 0:
                    # origin outside of line v3 -> v1
                    self._points.pop(1)
                    direction = v3_to_v1_normal
                    self._points.append(
                        self.shape1.furthest(direction)
                        - self.shape2.furthest(-direction)
                    )
                else:
                    # contains origin
                    self.contains_origin = True
            case _:
                raise ValueError("Can't evolve simplex >3 vertices")
