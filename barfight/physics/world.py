from collections import defaultdict
from dataclasses import dataclass
from functools import partial

from pyglet.math import Vec2

from .primitives import Collision, Rectangle

from .body import Body, BodyKind
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


class PhysicsWorld:
    def __init__(self, origin: Vec2, size: Vec2, max_depth=8):
        self.origin = origin
        self.size = size
        self.max_depth = max_depth
        self.bodies: list[Body | None] = []
        self.root = QuadTree(self.bodies, Rectangle(self.origin, self.size), self.max_depth)
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
            raise ValueError("Not within the boundary")

    def remove(self, body: Body):
        index = self.bodies.index(body)
        self.root.remove(index)
        self.bodies[index] = None

    def clear(self):
        self.bodies = []
        self.active_collisions = set()
        self.new_collisions = set()
        self.root = QuadTree(self.bodies, Rectangle(self.origin, self.size), self.max_depth)

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
            collisions = self.query(body.shape.boundary())
            for colliding_body in collisions:
                if colliding_body is body:
                    continue
                new_collisions.add(BroadCollision(body, colliding_body))

        return new_collisions
    
    def discrete_phase(self, broad_collisions: set[BroadCollision]) -> set[DiscreteCollision]:
        discrete_collisions = set()

        for bc in broad_collisions:
            if collision := bc.first.shape.penetration(bc.second.shape):
                discrete_collisions.add(DiscreteCollision(bc.first, bc.second, collision.penetration, collision.depth))

        return discrete_collisions

    def step(self, dt: float):
        broad_collisions = self.broad_phase()
        discrete_collisions = self.discrete_phase(broad_collisions)
        resolved_collisions = self.resolve(discrete_collisions)
        ended_collisions = broad_collisions - self.active_collisions
        #TODO Send collision ended events
        # self.active_collisions = self.new_collisions
        
        

    def resolve(self, collisions: set[DiscreteCollision]) -> set[tuple[Body, Body, bool]]:
        resolved_collisions = set()

        for collision in collisions:
            match collision.first.kind, collision.second.kind:
                case BodyKind.Dynamic, BodyKind.Static:
                    collision.first.shape.position -= collision.penetration
                    arbiter = Arbiter(collision.first, collision.second, False)    #TODO: Hard-coding first collision
                    resolved_collisions.add((collision.first, collision.second, arbiter))
                    self._call_position_change(collision.first)
                    self._call_on_collision(arbiter)
                case BodyKind.Dynamic, BodyKind.Sensor:
                    ...

        return resolved_collisions


        # for body in sorted(collisions, key=partial(closest_body, target.shape.center)):
        #     if target.layer & body.mask == 0 and body.layer and target.mask == 0:
        #         continue

        #     arbiter = Arbiter(
        #         target, body, (target, body) not in self.active_collisions
        #     )

        #     match body.kind:
        #         case BodyKind.Sensor:
        #             self._call_on_sensor(arbiter)
        #         case BodyKind.Static:
        #             if target.shape.overlaps(body.shape):
        #                 target.resolve_with(body)
        #                 self._call_position_change(target)
        #                 self._call_on_collision(arbiter)

    def query(self, area: Rectangle) -> list[Body]:
        return self.root.query(area)

    def query_with(self, area: Rectangle, layer: int) -> list[Body]:
        bodies = self.query(area)
        return [body for body in bodies if body.mask & layer != 0]

    def is_colliding(self, area: Rectangle) -> bool:
        return self.query(area) != []

    def is_colliding_with(self, area: Rectangle, layer: int) -> bool:
        return self.query_with(area, layer) != []

    def nearest(self, point: Vec2):
        return self.root.nearest(point)
