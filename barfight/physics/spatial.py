from math import inf
from typing import Self

from pyglet.math import Vec2

from .common import BoundingBox
from .body import Body
from .shapes import PointShape


class QuadTree:
    def __init__(self, bodies: list[Body], boundary: BoundingBox, capacity: int, max_depth: int = 8):
        self.bodies = bodies
        self.boundary = boundary
        self.capacity = capacity
        self.depth = max_depth
        self.children: set[int] = set()

        self.is_divided = False
        self.bottom_left: QuadTree | None = None
        self.bottom_right: QuadTree | None = None
        self.top_left: QuadTree | None = None
        self.top_right: QuadTree | None = None

    def insert(self, body_index: int) -> bool:
        if not self.boundary.overlaps(self.bodies[body_index].shape.boundary()):
            return False

        if self.depth <= 0 or (
            len(self.children) < self.capacity and not self.is_divided
        ):
            self.children.add(body_index)
            return True

        if not self.is_divided:
            self.subdivide()

        if self.bottom_left.insert(body_index):
            return True
        elif self.bottom_right.insert(body_index):
            return True
        elif self.top_left.insert(body_index):
            return True
        elif self.top_right.insert(body_index):
            return True
        else:
            self.children.add(body_index)
            return True

    def remove(self, body_index: int):
        self.children.remove(body_index)
        if self.is_divided:
            self.bottom_left.remove(body_index)
            self.bottom_right.remove(body_index)
            self.top_left.remove(body_index)
            self.top_right.remove(body_index)

            if not all(
                self.bottom_left.children,
                self.bottom_right.children,
                self.top_left.children,
                self.top_right.children,
            ):
                self.bottom_left = self.bottom_right = self.top_left = (
                    self.top_right
                ) = None
                self.is_divided = False

    def subdivide(self):
        left_x = self.boundary.min.x
        middle_x = self.boundary.min.x + (self.boundary.max.x - self.boundary.min.x) / 2
        right_x = self.boundary.max.x

        bottom_y = self.boundary.min.y
        middle_y = self.boundary.min.y + (self.boundary.max.y - self.boundary.min.y) / 2
        top_y = self.boundary.max.y

        self.bottom_left = QuadTree(
            BoundingBox(Vec2(left_x, bottom_y), Vec2(middle_x, middle_y)),
            self.capacity,
            self.depth - 1,
        )
        self.bottom_right = QuadTree(
            BoundingBox(Vec2(middle_x, bottom_y), Vec2(right_x, middle_y)),
            self.capacity,
            self.depth - 1,
        )
        self.top_left = QuadTree(
            BoundingBox(Vec2(left_x, middle_y), Vec2(middle_x, top_y)),
            self.capacity,
            self.depth - 1,
        )
        self.top_right = QuadTree(
            BoundingBox(Vec2(middle_x, middle_y), Vec2(right_x, top_y)),
            self.capacity,
            self.depth - 1,
        )

        self.is_divided = True

        current = self.children
        self.children = []
        for item in current:
            self.insert(item)

    def query(self, area: BoundingBox) -> list[Body]:
        if not self.boundary.overlaps(area):
            return []

        bodies = [self.bodies[body_index] for body_index in self.children if area.overlaps(self.bodies[body_index].shape.boundary())]

        if self.is_divided:
            bodies += (
                self.bottom_left.query(area)
                + self.bottom_right.query(area)
                + self.top_left.query(area)
                + self.top_right.query(area)
            )

        return bodies

    def _subdivisions_by_distance(self, point: Vec2) -> list[Self]:
        def node_distance(node: QuadTree) -> float:
            return point.position.distance(node.boundary.center)    # TODO: Uneccessary?

        return sorted(
            (self.bottom_left, self.bottom_right, self.top_left, self.top_right),
            key=node_distance,
        )

    def nearest(
        self,
        point: PointShape,
        best_distance: float = inf,
        closest: Body | None = None,
    ) -> tuple[float, Body]:
        for body_index in self.children:
            distance = point.position.distance(body.shape.center)
            if distance < best_distance:
                best_distance, closest = distance, body

        if self.is_divided:
            for node in self._subdivisions_by_distance(point):
                child_distance, child_body = node.nearest(point)
                if child_distance < best_distance:
                    best_distance, closest = child_distance, child_body

        return best_distance, closest

    def collisions(self, parent_bodies: list[Body]) -> list[tuple[Body, Body]]:
        colliding = []
        bodies = self.children + parent_bodies

        for first_body in bodies:
            for second_body in bodies:
                if first_body is second_body:
                    continue
                if not self.boundary.overlaps(
                    first_body.shape
                ) or not self.boundary.overlaps(second_body.shape):
                    continue
                if first_body.shape.overlaps(second_body.shape):
                    colliding.append((first_body, second_body))

        if self.is_divided:
            colliding += (
                self.bottom_left.collisions(bodies)
                + self.bottom_right.collisions(bodies)
                + self.top_left.collisions(bodies)
                + self.top_right.collisions(bodies)
            )

        return colliding
