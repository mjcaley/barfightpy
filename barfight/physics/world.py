from dataclasses import dataclass
from math import inf

from loguru import logger
from pyglet.math import Vec2

from barfight.physics.raycast import Ray

from .body import Body, BodyKind
from .primitives import Rectangle
from .response import Arbiter
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
    def __init__(self, origin: Vec2, size: Vec2, max_depth=8):
        self.origin = origin
        self.size = size
        self.max_depth = max_depth
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

    def discrete_phase(self, broad_collisions: set[CollisionPair]) -> tuple[set[CollisionPair], dict[CollisionPair, Resolution]]:
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
        broad_collisions = self.broad_phase()
        discrete_collisions, collision_resolutions = self.discrete_phase(broad_collisions)
        resolved_collisions, still_colliding = self.resolve(discrete_collisions, collision_resolutions)
        self.active_collisions = self.active_collisions - resolved_collisions | still_colliding

    def resolve(
        self, collisions: set[CollisionPair], resolutions: dict[CollisionPair, Resolution]
    ) -> tuple[set[CollisionPair], set[CollisionPair]]:
        resolved_collisions = set()
        still_colliding = set()

        for collision in collisions:
            match collision.first.kind, collision.second.kind:
                case BodyKind.Dynamic, BodyKind.Static:
                    if not collision.first.shape.collision(collision.second.shape):
                        resolved_collisions.add(CollisionPair(collision.first, collision.second))
                        continue
                    
                    collision.first.shape.position -= resolutions[collision].penetration
                    resolved_collisions.add(CollisionPair(collision.first, collision.second))
                    arbiter = Arbiter(collision.first, collision.second, collision not in self.active_collisions)
                    
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
                        resolved_collisions.add(CollisionPair(collision.first, collision.second))
                        continue

                    arbiter = Arbiter(collision.first, collision.second, collision not in self.active_collisions)
                    still_colliding.add(collision)
                    self._call_on_sensor(arbiter)

        return resolved_collisions, still_colliding

    def raycast(self, ray: Ray, kind: BodyKind) -> RaycastHit | None:
        closest_hit = None
        closest_body = None
        closest_distance = inf

        broad_bodies = self.query(ray.boundary())
        for body in broad_bodies:
            ...

        if hit := self.root.raycast(ray, kind):
            return RaycastHit(hit[0].point, hit[0].normal, hit[1])

    def query(self, area: Rectangle) -> list[Body]:
        return self.root.query(area)

    def is_colliding(self, area: Rectangle) -> bool:
        return self.query(area) != []

    def nearest(self, point: Vec2):
        return self.root.nearest(point)
