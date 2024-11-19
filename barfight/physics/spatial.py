from math import inf
from typing import Self

from loguru import logger
from pyglet.math import Vec2

from .body import Body, BodyKind
from .primitives import Rectangle
from .raycast import Ray, RayIntersection


class QuadTree:
    def __init__(
        self,
        bodies: list[Body | None],
        boundary: Rectangle,
        capacity: int = 20,
        max_depth: int = 8,
    ):
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

    @property
    def divisions(self) -> list[Self]:
        return [
            q
            for q in (
                self.bottom_left,
                self.bottom_right,
                self.top_left,
                self.top_right,
            )
            if q is not None
        ]

    def insert(self, body_index: int) -> bool:
        # If the body boundary is larger than the quadtree boundary, return False
        quadtree_rect = self.boundary
        body_rect = self.bodies[body_index].shape.boundary()
        if not (
            body_rect.origin.x >= quadtree_rect.origin.x
            and (body_rect.origin + body_rect.size).x
            <= (quadtree_rect.origin + quadtree_rect.size).x
            and body_rect.origin.y >= quadtree_rect.origin.y
            and (body_rect.origin + body_rect.size).y
            <= (quadtree_rect.origin + quadtree_rect.size).y
        ):
            breakpoint()
            logger.debug("Can't add, not in boundary, failed")
            return False

        # If we're at the bottom of the depth
        # AND
        # If we haven't reached capacity AND we're not divided
        if self.depth <= 0 or (
            len(self.children) < self.capacity and not self.is_divided
        ):
            logger.debug("Bottom of depth, adding")
            self.children.add(body_index)
            return True

        # At capacity, subdivide and try to insert into child quadtrees
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
            logger.debug("Adding into myself, added")
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
        self.bottom_left = QuadTree(
            self.bodies,
            Rectangle(
                self.boundary.origin, self.boundary.origin + self.boundary.size / 2
            ),
            self.capacity,
            self.depth - 1,
        )
        self.bottom_right = QuadTree(
            self.bodies,
            Rectangle(
                self.boundary.origin + Vec2(self.boundary.size.x / 2),
                self.boundary.origin
                + Vec2(self.boundary.size.x, self.boundary.size.y / 2),
            ),
            self.capacity,
            self.depth - 1,
        )
        self.top_left = QuadTree(
            self.bodies,
            Rectangle(
                self.boundary.origin + Vec2(0, self.boundary.size.y / 2),
                self.boundary.origin
                + Vec2(self.boundary.size.x / 2, self.boundary.size.y),
            ),
            self.capacity,
            self.depth - 1,
        )
        self.top_right = QuadTree(
            self.bodies,
            Rectangle(
                self.boundary.origin + self.boundary.size / 2,
                self.boundary.origin + self.boundary.size,
            ),
            self.capacity,
            self.depth - 1,
        )

        self.is_divided = True

        current = self.children
        self.children = set()
        for item in current:
            self.insert(item)

    def query(self, area: Rectangle) -> list[Body]:
        if not self.boundary.collision(area):
            return []

        bodies = [
            self.bodies[body_index]
            for body_index in self.children
            if area.collision(self.bodies[body_index].shape.boundary())
        ]

        if self.is_divided:
            bodies += (
                self.bottom_left.query(area)
                + self.bottom_right.query(area)
                + self.top_left.query(area)
                + self.top_right.query(area)
            )

        return bodies

    def nearest(
        self, point: Vec2, best_distance: float = inf, closest: Body | None = None
    ) -> tuple[float, Body]:
        for body_index in self.children:
            body = self.bodies[body_index]
            center_of_body = (
                body.shape.boundary().origin + body.shape.boundary().size / 2
            )

            ray = Ray(point, center_of_body - point)
            if intersection := ray.intersects(body.shape.primitive):
                distance = point.distance(intersection.point)

                if distance < best_distance:
                    best_distance, closest = distance, body

        if self.is_divided:
            for node in self.divisions:
                child_distance, child_body = node.nearest(point)
                if child_distance < best_distance:
                    best_distance, closest = child_distance, child_body

        return best_distance, closest

    def raycast(self, ray: Ray, kind: BodyKind) -> tuple[RayIntersection, Body] | None:
        if not ray.intersects(self.boundary):
            return None

        closest_hit = None
        closest_body = None
        closest_distance = inf
        for body_index in self.children:
            body = self.bodies[body_index]
            if body is None or body.kind != kind:
                continue
            if intersection := ray.intersects(body.shape.primitive):
                distance = ray.origin.distance(intersection.point)
                if distance < closest_distance:
                    closest_hit = intersection
                    closest_distance = distance
                    closest_body = body

        if self.is_divided:
            if bottom_left_result := self.bottom_left.raycast(ray, kind):
                if bottom_left_result[0] < closest_distance:
                    closest_distance = bottom_left_result[0]
                    closest_body = bottom_left_result[1]

            if bottom_left_result := self.bottom_right.raycast(ray, kind):
                if bottom_left_result[0] < closest_distance:
                    closest_distance = bottom_left_result[0]
                    closest_body = bottom_left_result[1]

            if top_left_result := self.top_left.raycast(ray, kind):
                if top_left_result[0] < closest_distance:
                    closest_distance = top_left_result[0]
                    closest_body = top_left_result[1]

            if top_right_result := self.top_right.raycast(ray, kind):
                if top_right_result[0] < closest_distance:
                    closest_distance = top_right_result[0]
                    closest_body = top_right_result[1]

        if closest_body is None:
            return None
        else:
            return closest_hit, closest_body

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
