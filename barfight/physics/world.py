from collections import defaultdict
from functools import partial
from pyglet.math import Vec2
from .spatial import QuadTree
from . import BoundingBox
from .body import Body, BodyKind
from . import Arbiter


# TODO: Get rid of
def closest_body(point: Vec2, body: Body) -> float:
    return body.shape.center.distance(point)


class PhysicsWorld:
    def __init__(self, min: Vec2, max: Vec2, max_depth=8):
        self.min = min
        self.max = max
        self.max_depth = max_depth
        self.root = QuadTree(BoundingBox(self.min, self.max), self.max_depth)
        self.active_collisions: set[tuple[Body, Body]] = set()
        self.position_change_callback = None
        self.on_collision_callback = None
        self.on_sensor_callback = None

    @property
    def boundary(self) -> BoundingBox:
        return self.root.boundary

    def insert(self, body: Body):
        if not self.root.insert(body):
            raise ValueError("Not within the boundary")

    def remove(self, body: Body):
        self.root.remove(body)

    def clear(self):
        self.root = QuadTree(BoundingBox(self.min, self.max), self.max_depth)

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

    def step(self):
        new_collisions = self.collisions()

        colliding: dict[Body, set[Body]] = defaultdict(set)
        for first, second in new_collisions:
            colliding[first].add(second)
            colliding[second].add(first)
        for target, collisions in colliding.items():
            self.resolve(target, collisions)

        self.active_collisions = new_collisions

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
