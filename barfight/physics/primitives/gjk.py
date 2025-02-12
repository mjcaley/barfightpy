from typing import Protocol

from pyglet.math import Vec2, Vec3
from loguru import logger


class GJKShape(Protocol):
    def furthest(self, direction: Vec2) -> Vec2: ...

    @property
    def center(self) -> Vec2: ...


def support(shape1: GJKShape, shape2: GJKShape, direction: Vec2) -> Vec2:
    furthest1 = shape1.furthest(direction)
    furthest2 = shape2.furthest(-direction)

    return furthest1 - furthest2


def triple_product(v1: Vec2, v2: Vec2, v3: Vec2) -> Vec2:
        a = Vec3(v1.x, v2.y, 0)
        b = Vec3(v2.x, v2.y, 0)
        c = Vec3(v3.x, v3.y, 0)

        first = a.cross(b)
        second = first.cross(c)

        return Vec2(second.x, second.y)


def is_past_origin(point: Vec2, direction: Vec2) -> float:
    return point.dot(direction) > 0


# Point that just got added is point A
class Simplex:
    def __init__(self, shape1: GJKShape, shape2: GJKShape):
        self.shape1 = shape1
        self.shape2 = shape2
        self._points = []
        self.search_direction = Vec2()
        self.finished = False
        self.colliding = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(shape1={repr(self.shape1)}, shape2={repr(self.shape2)})"
    
    def __str__(self) -> str:
        return f"Simplex - Points: {self._points}, Direction: {self.search_direction}, Colliding: {self.colliding}, Finished: {self.finished}"

    def support(self) -> Vec2:
        furthest1 = self.shape1.furthest(self.search_direction)
        furthest2 = self.shape2.furthest(-self.search_direction)

        return furthest1 - furthest2
    
    def gjk(self) -> bool:
        while result := self.evolve():
            match result:
                case "Finished":
                    return self.colliding
                case "Found intersection":
                    return self.colliding
                
    
    def evolve(self):
        if self.finished:
            return "Finished"

        match len(self._points):
            case 0:
                # Add the initial point
                self.search_direction = self.shape2.center - self.shape1.center
                a = self.support()
                self._points.append(a)
                
                return "Evolving"
            case 1:
                self.search_direction = -self.search_direction
                a = self.support()
                self._points.append(a)
                
                return "Evolving"
            case 2:
                c, b = self._points
                
                cb = b - c  # Line from the first two vertices
                c0 = -c     # Line from the first vertex to the origin

                # Get direction perpendicular to cb, towards the origin
                self.search_direction = triple_product(cb, c0, cb)
                a = self.support()
                self._points.append(a)
                
                return "Evolving"
            case 3:
                # Check if simplex containx the origin
                c, b, a = self._points

                a0 = -a     # Latest point to the origin
                ab = b - a
                ac = c - a

                ab_perp = triple_product(ac, ab, ab)
                ac_perp = triple_product(ab, ac, ac)

                if ab_perp.dot(a0) > 0:
                    # origin is outside the line ab
                    # remove point C and add a new support point in the direction of ab_perp
                    self._points.remove(c)
                    self.search_direction = ab_perp
                    self._points.append(self.support())
                elif ac_perp.dot(a0) > 0:
                    # the origin is outside line ac
                    # remove point B and add a new support point in the direction of ac_perp
                    self._points.remove(b)
                    self.search_direction = ac_perp
                    self._points.append(self.support())
                else:
                    self.finished = self.colliding = True
                    return "Found intersection"
            case _:
                self.finished = True
                raise ValueError("Simplex is in bad state")


def gjk(shape1: GJKShape, shape2: GJKShape):
    # First point added to simplex
    simplex = []
    direction = shape1.center - shape2.center
    a = support(shape1, shape2, direction)
    simplex.append(a)

    direction = -a

    while True:
        a = support(shape1, shape2, direction)
        if not is_past_origin(a, direction):
            return False    # Not past the origin, so intersection is not possible
        simplex.append(a)




# def line_case(simplex: list[Vec2], direction: Vec2) -> bool:
#     b, a = simplex
#     ab = b - a
#     ao = -a
#     ab_perp = triple_product(ab, ao, ab)
#     direction.set(ab_perp)  # TODO: Can't set direction here

#     return False


# def triangle_case(simplex: list[Vec2], direction: Vec2) -> bool:
#     c, b, a = simplex
    
#     ab = b - a
#     ac = c - a
#     ao = -a

#     ab_perp = triple_product(ac, ab, ab)
#     ac_perp = triple_product(ab, ac, ac)

#     if ab_perp.dot(ao) > 0:
#         simplex.remove(c)
#         direction = ab_perp # set
#     elif ac_perp.dot(ao) > 0:
#         simplex.remove(b)
#         direction = ac_perp # set
#         return False
#     return True


# def handle_simplex(simplex: list[Vec2], direction: Vec2) -> bool:
#     if len(simplex) == 2:
#         return line_case(simplex, direction)
    
#     return triangle_case(simplex, direction)


# def gjk(shape1: GJKShape, shape2: GJKShape) -> bool:
#     direction = (shape1.center - shape2.center).normalize()
#     simplex = [support(shape1, shape2, direction)]
#     direction = -simplex[0]

#     while True:
#         a = support(shape1, shape2, direction)
#         if a.dot(direction) < 0:
#             return False
#         simplex.append(a)
#         if handle_simplex(simplex, direction):
#             return True


# class Simplex:
#     def __init__(self, shape1: GJKShape, shape2: GJKShape):
#         self.shape1 = shape1
#         self.shape2 = shape2
#         self._vertices = []

#     def __len__(self) -> int:
#         return len(self._vertices)
    
#     @property
#     def a(self) -> Vec2 | None:
#         try:
#             return self._vertices[0]
#         except IndexError:
#             return None
        
#     @property
#     def b(self) -> Vec2 | None:
#         try:
#             return self._vertices[1]
#         except IndexError:
#             return None
        
#     @property
#     def c(self) -> Vec2 | None:
#         try:
#             return self._vertices[2]
#         except IndexError:
#             return None

#     def add(self, vertex: Vec2):
#         self._vertices.insert(0, vertex)

#     def remove(self, vertex: Vec2):
#         self._vertices.remove(vertex)


# def gjk2(shape1: GJKShape, shape2: GJKShape) -> bool:
#     simplex = Simplex(shape1, shape2)

#     direction = (shape1.center - shape2.center).normalize()
#     simplex.add(support(shape1, shape2, direction))
    
#     direction = -direction

#     while True:
#         logger.debug("Loop begin")
#         a = support(shape1, shape2, direction)
#         if a.dot(direction) < 0:
#             logger.debug("Vertex not inside origin {}", a)
#             return False
#         logger.debug("Adding vertex {}", a)
#         simplex.add(a)
#         breakpoint()

#         match len(simplex):
#             case 2:
#                 ab = simplex.b - simplex.a
#                 ao = -simplex.a
#                 ab_perp = triple_product(ab, ao, ab)
#                 direction = ab_perp
#                 logger.debug("New direction {}", direction)
#             case 3:    
#                 ab = simplex.b - simplex.a
#                 ac = simplex.c - simplex.a
#                 ao = -simplex.a

#                 ab_perp = triple_product(ac, ab, ab)
#                 ac_perp = triple_product(ab, ac, ac)

#                 if ab_perp.dot(ao) > 0:
#                     logger.debug("AB normal past origin, removing vertex c {}", simplex.c)
#                     simplex.remove(simplex.c)
#                     direction = ab_perp
#                     logger.debug("New direction {}", direction)
#                 elif ac_perp.dot(ao) > 0:
#                     logger.debug("AC normal past origin, removing vertex b {}", simplex.b)
#                     simplex.remove(simplex.b)
#                     direction = ac_perp
#                     logger.debug("New direction {}", direction)
#                 else:
#                     return True

        




# class Simplex:
#     def __init__(self, shape1: GJKShape, shape2: GJKShape):
#         self.shape1 = shape1
#         self.shape2 = shape2
#         self._points = []

#     @property
#     def a(self) -> Vec2 | None:
#         try:
#             return self._points[2]
#         except IndexError:
#             return None
        
#     @property
#     def b(self) -> Vec2 | None:
#         try:
#             return self._points[1]
#         except IndexError:
#             return None
        
#     @property
#     def c(self) -> Vec2 | None:
#         try:
#             return self._points[0]
#         except IndexError:
#             return None

#     @staticmethod
#     def triple_product(v1: Vec2, v2: Vec2, v3: Vec2) -> Vec2:
#         a = Vec3(v1.x, v2.y, 0)
#         b = Vec3(v2.x, v2.y, 0)
#         c = Vec3(v3.x, v3.y, 0)

#         first = a.cross(b)
#         second = first.cross(c)

#         return Vec2(second.x, second.y)

#     def add_support(self, direction: Vec2):
#         self._points.append(
#             self.shape1.furthest(direction) - self.shape2.furthest(-direction)
#         )

#     def evolve2(self) -> bool:
#         direction = (self.shape1.center - self.shape2.center).normalize()
#         self.add_support(direction)

#         direction = Vec2() - self.a

#         while True:
#             ...

#     def evolve(self):
#         match len(self._points):
#             case 0:
#                 direction = (self.shape1.center - self.shape2.center).normalize()
#                 self.add_support(direction)
#             case 1:
#                 direction = -(self.shape1.center - self.shape2.center).normalize()
#                 self.add_support(direction)
#             case 2:
#                 v1, v2 = self._points
#                 line = v2 - v1
#                 v1_to_origin = -v1

#                 direction = self.triple_product(line, v1_to_origin, line)
#                 self.add_support(direction)
#             case 3:
#                 v1, v2, v3 = self._points

#                 v3_to_origin = -v3
#                 v3_to_v2 = v2 - v3
#                 v3_to_v1 = v1 - v3

#                 v3_to_v2_normal: Vec2 = self.triple_product(
#                     v3_to_v1, v3_to_v2, v3_to_v2
#                 )
#                 v3_to_v1_normal: Vec2 = self.triple_product(
#                     v3_to_v2, v3_to_v1, v3_to_v1
#                 )

#                 if v3_to_v2_normal.dot(v3_to_origin) > 0:
#                     # origin outside of line v3 -> v2
#                     self._points.pop(0)
#                     direction = v3_to_v2_normal
#                     self.add_support(direction)
#                 elif v3_to_v1_normal.dot(v3_to_origin) < 0:
#                     # origin outside of line v3 -> v1
#                     self._points.pop(1)
#                     direction = v3_to_v1_normal
#                     self.add_support(direction)
#                 else:
#                     # contains origin
#                     self.contains_origin = True
#             case _:
#                 raise ValueError("Can't evolve simplex >3 vertices")
