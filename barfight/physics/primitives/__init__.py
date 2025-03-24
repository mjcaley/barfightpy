from copy import copy
from . import gjk
from .objects import (
    Collision,
    Circle,
    Line,
    LineSegment,
    OrientedRectangle,
    Point,
    Polygon,
    Rectangle,
    TimeOfImpact,
)
from .utility import Collision
from pyglet.math import Vec2


__all__ = [
    "Circle",
    "Line",
    "LineSegment",
    "OrientedRectangle",
    "Point",
    "Polygon",
    "Rectangle",
    "Collision",
    "colliding",
    "penetration",
    "time_of_impact",
]


type Primitive = Circle | OrientedRectangle | Point | Polygon | Rectangle


def colliding(primitive1: Primitive, primitive2: Primitive) -> Collision | None:
    if c := gjk.colliding(primitive1, primitive2):
        p = gjk.penetration(c)
        return Collision(p.normal, p.distance)
    
    return None


def time_of_impact(primitive1: Primitive, primitive2: Primitive, relative_velocity: Vec2, dt: float) -> TimeOfImpact | None:
    first_at_destination = middle = copy(primitive1)
    first_at_destination.center += relative_velocity * dt

    if early_hit := gjk.penetration(gjk.colliding(primitive1, primitive2)):
        return TimeOfImpact(0.0, early_hit.normal, early_hit.distance)
    
    late_hit = gjk.penetration(gjk.colliding(first_at_destination, primitive2))
    if not late_hit:
        return None

    dt_min = 0.0
    dt_mid = dt / 2
    dt_max = dt
    
    for depth in range(16):
        dt_mid = dt_min + ((dt_max - dt_min) / 2)
        middle.center = primitive1.center
        middle.center += relative_velocity * dt_mid

        if colliding(middle, primitive2):
            dt_max = dt_mid
        else:
            dt_min = dt_mid
    
    if middle_hit := gjk.penetration(gjk.colliding(middle, primitive2)):
        return TimeOfImpact(dt_mid, middle_hit.normal, middle_hit.distance)
    else:
        return TimeOfImpact(dt_min, late_hit.normal, late_hit.distance)
