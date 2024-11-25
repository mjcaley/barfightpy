from dataclasses import dataclass

from loguru import logger
from pyglet.math import Vec2

from barfight.physics.raycast import Ray

from .body import Body, BodyKind
from .primitives import Rectangle
from .response import Arbiter
from .spatial import QuadTree


@dataclass(frozen=True)
class BroadCollision:
    first: Body
    second: Body


@dataclass(frozen=True)
class DiscreteCollision:
    first: Body
    second: Body
    penetration: Vec2
    depth: float

    def __hash__(self):
        return hash((self.first, self.second))
    

@dataclass(frozen=True)
class RaycastHit:
    point: Vec2
    normal: Vec2
    body: Body


class PhysicsWorld:
    def __init__(self, origin: Vec2, size: Vec2, max_depth=8):
        self.origin = origin
        self.size = size
        self.max_depth = max_depth
        self.bodies: list[Body | None] = []
        self.root = QuadTree(
            self.bodies, Rectangle(self.origin, self.size), self.max_depth
        )
        self.active_collisions: set[tuple[Body, Body]] = set()
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
            breakpoint()
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

    def broad_phase(self) -> set[BroadCollision]:
        new_collisions = set()
        for body in self.bodies:
            if body is None:
                continue
            collisions = self.query(body.shape.boundary())
            for colliding_body in collisions:
                if colliding_body is body:
                    continue
                new_collisions.add(BroadCollision(body, colliding_body))

        return new_collisions

    def discrete_phase(
        self, broad_collisions: set[BroadCollision]
    ) -> set[DiscreteCollision]:
        discrete_collisions = set()

        for bc in broad_collisions:
            if collision := bc.first.shape.penetration(bc.second.shape):
                discrete_collisions.add(
                    DiscreteCollision(
                        bc.first, bc.second, collision.penetration, collision.depth
                    )
                )

        return discrete_collisions

    def step(self, dt: float):
        broad_collisions = self.broad_phase()
        discrete_collisions = self.discrete_phase(broad_collisions)
        resolved_collisions = self.resolve(discrete_collisions)
        # ended_collisions = broad_collisions - self.active_collisions
        # TODO Send collision ended events
        # self.active_collisions = self.new_collisions

        self.move(dt)

    def resolve(
        self, collisions: set[DiscreteCollision]
    ) -> set[tuple[Body, Body, bool]]:
        resolved_collisions = set()

        for collision in collisions:
            match collision.first.kind, collision.second.kind:
                case BodyKind.Dynamic, BodyKind.Static:
                    if not collision.first.shape.collision(collision.second.shape):
                        # Collision already resolved
                        continue
                    collision.first.shape.position -= collision.penetration
                    arbiter = Arbiter(
                        collision.first, collision.second, False
                    )  # TODO: Hard-coding first collision
                    logger.debug(
                        "Collision resolved",
                        body1=collision.first,
                        body2=collision.second,
                        penetration=collision.penetration,
                    )
                    resolved_collisions.add(
                        (collision.first, collision.second, arbiter)
                    )
                    # breakpoint()
                    self._call_position_change(collision.first)
                    self._call_on_collision(arbiter)
                case BodyKind.Dynamic, BodyKind.Sensor:
                    ...

        return resolved_collisions

    def move(self, dt: float):
        for body in self.bodies:
            if body is None or body.kind != BodyKind.Dynamic:
                continue
            ray = Ray(body.shape.boundary().center, body.velocity * dt)
            # self.raycast

    def raycast(self, ray: Ray, kind: BodyKind) -> RaycastHit | None:
        if hit := self.root.raycast(ray, kind):
            return RaycastHit(hit[0].point, hit[0].normal, hit[1])

    def query(self, area: Rectangle) -> list[Body]:
        return self.root.query(area)

    def is_colliding(self, area: Rectangle) -> bool:
        return self.query(area) != []

    def nearest(self, point: Vec2):
        return self.root.nearest(point)
