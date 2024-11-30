from dataclasses import dataclass
from functools import singledispatchmethod
from math import cos, inf, isnan, sin, sqrt

from pyglet.math import Vec2

from .primitives import Circle, Line, LineSegment, OrientedRectangle, Rectangle


@dataclass(frozen=True)
class RayIntersection:
    point: Vec2
    normal: Vec2
    distance: float


class Ray:
    def __init__(
        self, origin: Vec2 = None, direction: Vec2 = None, max_distance: float = 1.0
    ):
        self.origin = origin or Vec2()
        self._direction = (direction or Vec2()).normalize()
        self.max_distance = max_distance

    def boundary(self) -> Rectangle:
        ray_start = self.origin
        ray_end = self.direction.from_magnitude(self.max_distance) + self.origin

        return Rectangle(
            Vec2(min(ray_start.x, ray_end.x), min(ray_start.y, ray_end.y)),
            Vec2(max(ray_start.x, ray_end.x), max(ray_start.y, ray_end.y)),
        )

    @property
    def direction(self) -> Vec2:
        return self._direction

    @direction.setter
    def _(self, value: Vec2):
        self._direction = value.normalize()

    @singledispatchmethod
    def intersects(self, _) -> RayIntersection | None:
        raise NotImplementedError

    @intersects.register
    def _(self, line: Line) -> RayIntersection | None:
        # Calculate the determinant
        det = self.direction.x * line.direction.y - self.direction.y * line.direction.x

        # If determinant is zero, lines are parallel
        if abs(det) < 1e-6:
            return None

        t = (
            (line.base.x - self.origin.x) * line.direction.y
            - (line.base.y - self.origin.y) * line.direction.x
        ) / det

        # Check if intersection point is in front of ray origin
        if t >= 0:
            hit = self.origin + self.direction * t
            normal = Vec2(-line.direction.y, line.direction.x).normalize()
            distance = self.origin.distance(hit)
            return RayIntersection(hit, normal, distance)

        return None

    @intersects.register
    def _(self, line_segment: LineSegment) -> RayIntersection | None:
        direction = line_segment.point2 - line_segment.point1

        # Calculate the determinant
        det = self.direction.x * direction.y - self.direction.y * direction.x

        # If determinant is zero, ray and line segment are parallel
        if abs(det) < 1e-6:
            return None

        t = (
            (line_segment.point1.x - self.origin.x) * direction.y
            - (line_segment.point1.y - self.origin.y) * direction.x
        ) / det
        u = (
            (line_segment.point1.x - self.origin.x) * self.direction.y
            - (line_segment.point1.y - self.origin.y) * self.direction.x
        ) / det

        # Check if intersection is within the line segment and in front of ray origin
        if 0 <= u <= 1 and t >= 0:
            hit = self.origin + self.direction * t
            normal = Vec2(-direction.y, direction.x).normalize()
            distance = self.origin.distance(hit)

            return RayIntersection(hit, normal, distance)

        return None

    @intersects.register
    def _(self, circle: Circle) -> RayIntersection | None:
        f = self.origin - circle.center
        a = self.direction.dot(self.direction)
        b = 2 * f.dot(self.direction)
        c = f.dot(f) - circle.radius * circle.radius

        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None  # No intersection

        t = (-b - sqrt(discriminant)) / (2 * a)
        if t < 0:
            return None  # Intersection behind ray origin

        hit = self.origin + self.direction * t
        normal = (hit - circle.center).normalize()
        distance = self.origin.distance(hit)

        return RayIntersection(hit, normal, distance)

    @intersects.register
    def _(self, rectangle: Rectangle) -> RayIntersection | None:
        t_near = Vec2(
            (rectangle.origin.x - self.origin.x) / self.direction.x
            if self.direction.x != 0
            else -inf,
            (rectangle.origin.y - self.origin.y) / self.direction.y
            if self.direction.y != 0
            else -inf,
        )
        t_far = Vec2(
            (rectangle.origin.x + rectangle.size.x - self.origin.x) / self.direction.x
            if self.direction.x != 0
            else inf,
            (rectangle.origin.y + rectangle.size.y - self.origin.y) / self.direction.y
            if self.direction.y != 0
            else inf,
        )

        if isnan(t_far.y) or isnan(t_far.x):
            return None

        if t_near.x > t_far.x:
            t_near.x, t_far.x = t_far.x, t_near.x
        if t_near.y > t_far.y:
            t_near.y, t_far.y = t_far.y, t_near.y

        if t_near.x > t_far.y or t_near.y > t_far.x:
            return None

        t_hit = max(t_near.x, t_near.y)

        if t_hit < 0:
            return None

        hit = self.origin + self.direction * t_hit
        distance = self.origin.distance(hit)
        if t_near.x > t_near.y:
            normal = Vec2(-1 if self.direction.x > 0 else 1, 0)
        else:
            normal = Vec2(0, -1 if self.direction.y > 0 else 1)

        return RayIntersection(hit, normal, distance)

    @intersects.register
    def _(self, rectangle: OrientedRectangle) -> RayIntersection | None:
        # Transform ray to rectangle's local space
        local_origin = self.origin - rectangle.center
        local_origin = Vec2(
            local_origin.x * cos(-rectangle.rotation)
            - local_origin.y * sin(-rectangle.rotation),
            local_origin.x * sin(-rectangle.rotation)
            + local_origin.y * cos(-rectangle.rotation),
        )
        local_direction = Vec2(
            self.direction.x * cos(-rectangle.rotation)
            - self.direction.y * sin(-rectangle.rotation),
            self.direction.x * sin(-rectangle.rotation)
            + self.direction.y * cos(-rectangle.rotation),
        )

        local_ray = Ray(local_origin, local_direction)
        local_rect = Rectangle(
            Vec2(-rectangle.half_extent.x, -rectangle.half_extent.y),
            rectangle.half_extent * 2,
        )

        local_hit = local_ray.intersects(local_rect)
        if local_hit is None:
            return None

        # Transform hit point back to world space
        world_hit = (
            Vec2(
                local_hit.x * cos(rectangle.rotation)
                - local_hit.y * sin(rectangle.rotation),
                local_hit.x * sin(rectangle.rotation)
                + local_hit.y * cos(rectangle.rotation),
            )
            + rectangle.center
        )

        world_normal = Vec2(
            local_hit.normal.x * cos(rectangle.rotation)
            - local_hit.normal.y * sin(rectangle.rotation),
            local_hit.normal.x * sin(rectangle.rotation)
            + local_hit.normal.y * cos(rectangle.rotation),
        )

        world_distance = self.origin.distance(world_hit)

        return RayIntersection(world_hit, world_normal, world_distance)
