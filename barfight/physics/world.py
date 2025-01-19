from copy import copy
from dataclasses import dataclass
from functools import singledispatchmethod
from math import inf
from typing import Any

from loguru import logger
from pyglet.math import Vec2

from .body import Body, BodyKind
from .primitives import Circle, OrientedRectangle, Rectangle
from .raycast import Ray
from .response import Arbiter
from .shapes import CircleShape, OrientedRectangleShape
from .spatial import QuadTree


@dataclass(frozen=True)
class CollisionPair:
    first: Body
    second: Body


@dataclass
class Resolution:
    penetration: Vec2
    depth: float


@dataclass(frozen=True)
class RaycastHit:
    point: Vec2
    normal: Vec2
    body: Body


class PhysicsWorld:
    def __init__(self, origin: Vec2, size: Vec2, max_depth=8, step_iterations=8):
        self.origin = origin
        self.size = size
        self.max_depth = max_depth
        self.step_iterations = step_iterations

        self.bodies: list[Body | None] = []
        self.root = QuadTree(
            self.bodies, Rectangle(self.origin, self.size), self.max_depth
        )
        self.active_collisions: set[CollisionPair] = set()
        self.position_change_callback = None
        self.on_collision_callback = None
        self.on_sensor_callback = None

    @property
    def boundary(self) -> Rectangle:
        return self.root.boundary

    def add(self, body: Body):
        try:
            index = self.bodies.index(None)
            self.bodies[index] = body
        except ValueError:
            self.bodies.append(body)
            index = len(self.bodies) - 1

        if not self.root.insert(index):
            raise ValueError("Not within the boundary")

    def remove(self, body: Body):
        index = self.bodies.index(body)
        self.root.remove(index)
        self.bodies[index] = None

    def clear(self):
        self.bodies = []
        self.active_collisions = set()
        self.new_collisions = set()
        self.root = QuadTree(
            self.bodies, Rectangle(self.origin, self.size), self.max_depth
        )

    def _call_position_change(self, body: Body):
        if self.position_change_callback:
            self.position_change_callback(body)

    def _call_on_collision(self, arbiter: Arbiter):
        if self.on_collision_callback:
            self.on_collision_callback(arbiter)

    def _call_on_sensor(self, arbiter: Arbiter):
        if self.on_sensor_callback:
            self.on_sensor_callback(arbiter)

    def broad_phase(self) -> set[CollisionPair]:
        new_collisions = set()
        for body in self.bodies:
            if body is None:
                continue
            collisions = self.query(body.shape.boundary())
            for colliding_body in collisions:
                if colliding_body is body:
                    continue
                new_collisions.add(CollisionPair(body, colliding_body))

        return new_collisions

    def discrete_phase(
        self, broad_collisions: set[CollisionPair]
    ) -> tuple[set[CollisionPair], dict[CollisionPair, Resolution]]:
        discrete_collisions = set()
        collision_resolution = {}

        for bc in broad_collisions:
            if collision := bc.first.shape.penetration(bc.second.shape):
                pair = CollisionPair(bc.first, bc.second)
                resolution = Resolution(collision.penetration, collision.depth)
                discrete_collisions.add(pair)
                collision_resolution[pair] = resolution

        return discrete_collisions, collision_resolution

    def step(self, dt: float):
        self.move(dt)
        self.collisions()

    def resolve(
        self,
        collisions: set[CollisionPair],
        resolutions: dict[CollisionPair, Resolution],
    ) -> tuple[set[CollisionPair], set[CollisionPair]]:
        resolved_collisions = set()
        still_colliding = set()

        for collision in collisions:
            match collision.first.kind, collision.second.kind:
                case BodyKind.Dynamic, BodyKind.Static:
                    if not collision.first.shape.collision(collision.second.shape):
                        resolved_collisions.add(
                            CollisionPair(collision.first, collision.second)
                        )
                        continue

                    collision.first.shape.position -= resolutions[collision].penetration
                    resolved_collisions.add(
                        CollisionPair(collision.first, collision.second)
                    )
                    arbiter = Arbiter(
                        collision.first,
                        collision.second,
                        collision not in self.active_collisions,
                    )

                    logger.debug(
                        "Collision resolved {body1} {body2} {penetration}",
                        body1=collision.first,
                        body2=collision.second,
                        penetration=resolutions[collision].penetration,
                    )
                    self._call_position_change(collision.first)
                    self._call_on_collision(arbiter)
                case BodyKind.Dynamic, BodyKind.Sensor:
                    if not collision.first.shape.collision(collision.second.shape):
                        resolved_collisions.add(
                            CollisionPair(collision.first, collision.second)
                        )
                        continue

                    arbiter = Arbiter(
                        collision.first,
                        collision.second,
                        collision not in self.active_collisions,
                    )
                    still_colliding.add(collision)
                    self._call_on_sensor(arbiter)

        return resolved_collisions, still_colliding

    def raycast(self, ray: Ray, kind: BodyKind) -> RaycastHit | None:
        closest_hit = None
        closest_body = None
        closest_distance = inf

        for body in self.query(ray.boundary()):
            if body.kind != kind:
                continue
            if intersection := ray.intersects(body.shape.primitive):
                if intersection.distance < closest_distance:
                    closest_hit = intersection
                    closest_distance = intersection.distance
                    closest_body = body

        if closest_body is None or closest_hit is None:
            return None

        return RaycastHit(closest_hit.point, closest_hit.normal, closest_body)

    def collisions(self):
        for _ in range(self.step_iterations):
            broad_collisions = self.broad_phase()
            discrete_collisions, collision_resolutions = self.discrete_phase(
                broad_collisions
            )
            resolved_collisions, still_colliding = self.resolve(
                discrete_collisions, collision_resolutions
            )
            self.active_collisions = (
                self.active_collisions - resolved_collisions | still_colliding
            )

    @staticmethod
    def _movement_boundary(body: Body, velocity: Vec2) -> Rectangle:
        current_shape = body.shape
        target_shape = copy(current_shape)
        target_shape.position += velocity
        min_origin = Vec2(
            min(current_shape.boundary().origin.x, target_shape.boundary().origin.x),
            min(current_shape.boundary().origin.y, target_shape.boundary().origin.y),
        )
        max_x = max(
            current_shape.boundary().top_right_vertex.x,
            target_shape.boundary().top_right_vertex.x,
        )
        max_y = max(
            current_shape.boundary().top_right_vertex.y,
            target_shape.boundary().top_right_vertex.y,
        )
        max_size = Vec2(max_x - min_origin.x, max_y - min_origin.y)

        return Rectangle(min_origin, max_size)

    def _move_body(self, body: Body, leftover: Vec2, max_depth: int = 50) -> Vec2:
        if not max_depth:
            return Vec2()

        current_shape = body.shape
        boundary = self._movement_boundary(body, leftover)
        broad_collisions = self.query(boundary)

        had_collision = False
        for collision in broad_collisions:
            if collision is body:
                continue
            if collision.kind != BodyKind.Static:
                continue

            minkowski_difference = collision.shape.minkowski_difference(current_shape)
            if minkowski_difference.collision(Vec2()):
                logger.debug("Minkoski difference colliding, skipping")
                continue

            ray = Ray(Vec2(), leftover.normalize(), leftover.mag)
            intersection = ray.intersects(minkowski_difference)
            if intersection:
                had_collision = True
                breakpoint()
                dot_product = leftover.dot(intersection.normal)
                sliding_vector = leftover - (intersection.normal * dot_product)
                leftover = sliding_vector

                logger.debug(
                    "Minkowski intersection found - {intersection}\nVelocity changed to {velocity}",
                    intersection=intersection,
                    velocity=leftover,
                )
            else:
                logger.debug("Minkowski - No intersection found")

        if had_collision:
            return self._move_body(body, leftover, max_depth - 1)
        return leftover

    def move(self, dt: float):
        for body in self.bodies:
            if body is None:
                continue
            if body.kind != BodyKind.Dynamic:
                continue

            logger.debug(
                "Begin moving {body}, velocity: {velocity}, position: {position}",
                body=body,
                velocity=body.velocity,
                position=body.position,
            )
            # if body.velocity != Vec2():
            #     breakpoint()
            final_velocity = self._move_body(body, body.velocity * dt)
            body.velocity = final_velocity
            body.position += final_velocity
            logger.debug(
                "End moving {body}, velocity: {velocity}, position: {position}",
                body=body,
                velocity=body.velocity,
                position=body.position,
            )
            self._call_position_change(body)

    def query(self, area: Rectangle) -> list[Body]:
        return self.root.query(area)

    @singledispatchmethod
    def is_colliding(self, primitive: Any) -> bool:
        raise NotImplementedError

    @is_colliding.register
    def _(self, primitive: Rectangle) -> bool:
        return self.query(primitive) != []

    @is_colliding.register
    def _(self, primitive: OrientedRectangle) -> bool:
        shape = OrientedRectangleShape(
            primitive.center, primitive.half_extent, primitive.rotation
        )
        for body in self.query(shape.boundary()):
            if body.shape.collision(shape):
                return True

        return False

    @is_colliding.register
    def _(self, primitive: Vec2) -> bool:
        for body in self.query(Rectangle(primitive, Vec2())):
            if body.shape.collision(primitive):
                return True

        return False

    @is_colliding.register
    def _(self, primitive: Circle) -> bool:
        shape = CircleShape(primitive.center, primitive.radius)
        for body in self.query(shape.boundary()):
            if body.shape.collision(shape):
                return True

        return False

    def nearest(self, point: Vec2) -> Body | None:
        return self.root.nearest(point)[1]
