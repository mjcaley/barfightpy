from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol

from pyglet.math import Vec2, Vec3


def perpendicular(v: Vec2) -> Vec2:
    return Vec2(-v.y, v.x)


class GJKShape(Protocol):
    def furthest(self, direction: Vec2) -> Vec2: ...

    @property
    def center(self) -> Vec2: ...


@dataclass
class Simplex:
    points: list[Vec2] = field(default_factory=list)

    def add(self, point: Vec2):
        self.points.append(point)

    def remove(self, index: int):
        self.points.pop(index)


@dataclass
class Collision:
    shape1: GJKShape
    shape2: GJKShape
    simplex: list[Vec2]


class GJKState:
    def __init__(self, shape1: GJKShape, shape2: GJKShape):
        self.shape1 = shape1
        self.shape2 = shape2
        
        # Get initial support point in any direction (using vector between centers)
        self.direction = self.shape1.center - self.shape2.center
        if self.direction.length() == 0:
            self.direction = Vec2(1, 0)
            
        self.simplex = Simplex([support(shape1, shape2, self.direction)])
        self.direction = -self.direction  # Next search toward origin

    def handle_simplex(self) -> bool:
        if len(self.simplex.points) == 2:
            return self.line_case()
        return self.triangle_case()
    
    def line_case(self) -> bool:
        b, a = self.simplex.points  # a is the latest point
        ab = b - a
        ao = -a  # Vector from a to origin
        
        # Get perpendicular to ab pointing toward origin
        if same_direction(perpendicular(ab), ao):
            self.direction = perpendicular(ab)
        else:
            self.direction = -perpendicular(ab)
        return False

    def triangle_case(self) -> bool:
        c, b, a = self.simplex.points  # a is the latest point
        ab = b - a
        ac = c - a
        ao = -a  # Vector from a to origin
        
        # Compute perpendicular vectors for edges
        ab_perp = triple_product(ac, ab, ab)
        ac_perp = triple_product(ab, ac, ac)
        
        if same_direction(ab_perp, ao):
            self.simplex.remove(2)  # Remove c
            self.direction = ab_perp
            return False
        elif same_direction(ac_perp, ao):
            self.simplex.remove(1)  # Remove b
            self.direction = ac_perp
            return False
        return True  # Origin is inside triangle

    def colliding(self) -> Collision | None:
        while True:
            point = support(self.shape1, self.shape2, self.direction)
            
            # If we didn't pass the origin, no collision
            if point.dot(self.direction) <= 0:
                return None
                
            self.simplex.add(point)
            
            # Check if we contain origin and update direction
            if self.handle_simplex():
                return Collision(self.shape1, self.shape2, self.simplex.points)


def support(shape1: GJKShape, shape2: GJKShape, direction: Vec2) -> Vec2:
    """Get furthest point of Minkowski difference in given direction"""
    return shape1.furthest(direction) - shape2.furthest(-direction)


def same_direction(a: Vec2, b: Vec2) -> bool:
    """Check if vectors point in roughly the same direction"""
    return a.dot(b) > 0


def triple_product(a: Vec2, b: Vec2, c: Vec2) -> Vec2:
    """Compute perpendicular vector to triangle defined by a, b, c"""
    ac = a.cross(c)  # Treat as z-component
    return Vec2(-b.y * ac, b.x * ac)


def colliding(shape1: GJKShape, shape2: GJKShape) -> Collision | None:
    """Implementation of the GJK algorithm.
    
    References
    ==========
    https://www.youtube.com/watch?v=ajv46BSqcK4
    """

    state = GJKState(shape1, shape2)
    
    return state.colliding()


def penetration(collision: Collision) -> Vec2:
    """EPA (Expanding Polytope Algorithm) implementation.
    
    References
    ==========


    https://winter.dev/articles/epa-algorithm
    https://www.youtube.com/watch?v=0XQ2FSz3EK8&t=344s
    """
    
    polytope = collision.simplex.copy()
    
    while True:
        # Find closest edge to origin
        min_dist = float('inf')
        min_normal = Vec2(0, 0)
        min_index = 0
        
        for i in range(len(polytope)):
            j = (i + 1) % len(polytope)
            edge = polytope[j] - polytope[i]
            normal = Vec2(-edge.y, edge.x).normalize()
            
            # Make sure normal points toward origin
            if normal.dot(polytope[i]) < 0:
                normal = -normal
                
            dist = normal.dot(polytope[i])
            
            if dist < min_dist:
                min_dist = dist
                min_normal = normal
                min_index = j
                
        # Get support point in direction of edge normal
        support_point = support(collision.shape1, collision.shape2, min_normal)
        support_dist = min_normal.dot(support_point)
        
        # Check if we're done (within tolerance)
        if abs(support_dist - min_dist) < 0.0001:
            return min_normal * min_dist
            
        # Insert support point into polytope
        polytope.insert(min_index, support_point)
