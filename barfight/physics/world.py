from collections import defaultdict
from functools import partial

from pyglet.math import Vec2

from .primitives import Rectangle

from .body import Body, BodyKind
from .response import Arbiter
from .spatial import QuadTree



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
        self.bodies.append(body)
        index = len(self.bodies)
        if not self.root.insert(index):
            raise ValueError("Not within the boundary")

    def remove(self, body: Body):
        self.root.remove(self.bodies.index(body))

    def clear(self):
        self.bodies = []
        self.active_collisions = set()
        self.new_collisions = set()
        self.root = QuadTree(self.bodies, Rectangle(self.origin, self.size), self.max_depth)

    def collisions(self) -> list[tuple[Body, Body]]:
        return self.root.collisions([])

    def _call_position_change(self, body: Body):
        if self.position_change_callback:
            self.position_change_callback(body)

    def _call_on_collision(self, arbiter: Arbiter):
        if self.on_collision_callback:
            self.on_collision_callback(arbiter)

    def _call_on_sensor(self, arbiter: Arbiter):
        if self.on_sensor_callback:
            self.on_sensor_callback(arbiter)

    def broad_phase(self) -> set[tuple[Body, Body]]:
        new_collisions = set()
        for body in self.bodies:
            if body is None or body.kind != BodyKind.Dynamic:
                continue
            collisions = self.query(body.shape.boundary())
            for colliding_body in collisions:
                new_collisions.add((body, colliding_body))

        return new_collisions
    
    def discrete_phase(self, broad_collisions: set[tuple[Body, Body]]):
        discrete_collisions = set()

        for first_body, second_body in broad_collisions:
            if not first_body.shape.collision(second_body.shape):
                continue
            discrete_collisions.add((first_body, second_body))

    def step(self, dt: float):
        broad_collisions = self.broad_phase()
        discrete_collisions = self.discrete_phase(broad_collisions)
        resolved_collisions = self.resolve(discrete_collisions)

        
        ended_collisions = broad_collisions - self.active_collisions
        #TODO Send collision ended events
        self.active_collisions = self.new_collisions
        
        

    def resolve(self, target: Body, collisions: set[Body]):
        for body in sorted(collisions, key=partial(closest_body, target.shape.center)):
            if target.layer & body.mask == 0 and body.layer and target.mask == 0:
                continue

            arbiter = Arbiter(
                target, body, (target, body) not in self.active_collisions
            )

            match body.kind:
                case BodyKind.Sensor:
                    self._call_on_sensor(arbiter)
                case BodyKind.Static:
                    if target.shape.overlaps(body.shape):
                        target.resolve_with(body)
                        self._call_position_change(target)
                        self._call_on_collision(arbiter)

    def query(self, area: BoundingBox) -> list[Body]:
        return self.root.query(area)

    def query_with(self, area: BoundingBox, layer: int) -> list[Body]:
        bodies = self.query(area)
        return [body for body in bodies if body.mask & layer != 0]

    def is_colliding(self, area: BoundingBox) -> bool:
        return self.query(area) != []

    def is_colliding_with(self, area: BoundingBox, layer: int) -> bool:
        return self.query_with(area, layer) != []

    def nearest(self, point: Vec2):
        return self.root.nearest(point)
