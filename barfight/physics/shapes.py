from math import inf
from typing import Protocol, Self

from pyglet.math import Vec2

from .primitives import (
    Primitive,
    Circle,
    Collision,
    OrientedRectangle,
    Point,
    Polygon,
    Rectangle,
    colliding,
)


class ShapeProtocol(Protocol):
    @property
    def primitive(self) -> Primitive: ...

    @property
    def position(self) -> Vec2: ...

    @position.setter
    def position(self, value: Vec2): ...

    def boundary(self) -> Rectangle: ...

    def collision(self, shape: Self) -> bool: ...

    def penetration(self, shape: Self) -> Collision | None: ...

    def __copy__(self) -> Self: ...


class Shape:
    def __init__(self, primitive: Primitive):
        self._primitive = primitive

    @property
    def primitive(self) -> Primitive:
        return self._primitive
    
    @property
    def position(self) -> Vec2:
        return self.primitive.center
    
    @position.setter
    def position(self, value: Vec2):
        self.primitive.center = value

    def collision(self, shape: Self) -> bool:
        if _ := colliding(self.primitive, shape.primitive):
            return True
        else:
            return False
        
    def penetration(self, shape: Self) -> Collision | None:
        return colliding(self.primitive, shape.primitive)


class PointShape(Shape):
    def __init__(self, point: Vec2):
        super().__init__(point)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(point={self._primitive.point})"

    def boundary(self) -> Rectangle:
        return Rectangle(self.primitive, Vec2())


class RectangleShape:
    def __init__(self, origin: Vec2 = None, size: Vec2 = None):
        origin = origin or Vec2()
        size = size or Vec2()
        super().__init__(Rectangle(origin, size))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(primitive: {self.primitive})"

    @property
    def primitive(self) -> Rectangle:
        return self._primitive

    @property
    def position(self) -> Vec2:
        return self._primitive.center

    @position.setter
    def position(self, value: Vec2):
        self._primitive.center = value

    def boundary(self) -> Rectangle:
        return self._primitive

    def collision(self, shape: ShapeProtocol) -> bool:
        return self.primitive.collision(shape.primitive)

    def penetration(self, shape: ShapeProtocol) -> Collision | None:
        return self.primitive.penetration(shape.primitive)

    def minkowski_difference(self, shape: ShapeProtocol) -> PrimitiveType:
        return self.primitive.minkowski_difference(shape.primitive)

    def __copy__(self) -> Self:
        return RectangleShape(self._primitive.origin, self._primitive.size)


class OrientedRectangleShape:
    def __init__(
        self, center: Vec2 = None, half_extent: Vec2 = None, rotation: float = 0
    ):
        center = center or Vec2()
        half_extent = half_extent or Vec2()
        self._primitive = OrientedRectangle(center, half_extent, rotation)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(primitive: {self.primitive})"

    @property
    def primitive(self) -> OrientedRectangle:
        return self._primitive

    @property
    def position(self) -> Vec2:
        return self._primitive.center

    @position.setter
    def position(self, value: Vec2):
        self._primitive.center = value

    def boundary(self) -> Rectangle:
        min_x = inf
        max_x = -inf
        min_y = inf
        max_y = -inf

        for vertex in self._primitive.vertices():
            min_x = min(min_x, vertex.x)
            max_x = max(max_x, vertex.x)
            min_y = min(min_y, vertex.y)
            max_y = max(max_y, vertex.y)

        return Rectangle(Vec2(min_x, min_y), Vec2(max_x - min_x, max_y - min_y))

    def collision(self, shape: ShapeProtocol) -> bool:
        return self.primitive.collision(shape.primitive)

    def penetration(self, shape: ShapeProtocol) -> Collision | None:
        return self.primitive.penetration(shape.primitive)

    def minkowski_difference(self, shape: ShapeProtocol) -> PrimitiveType:
        return self.primitive.minkowski_difference(shape.primitive)

    def __copy__(self) -> Self:
        return OrientedRectangleShape(
            self._primitive.center,
            self._primitive.half_extent,
            self._primitive.rotation,
        )


class CircleShape:
    def __init__(self, center: Vec2 = None, radius: float = 0):
        center = center or Vec2()
        self._primitive = Circle(center, radius)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(primitive: {self.primitive})"

    @property
    def primitive(self) -> Circle:
        return self._primitive

    @property
    def position(self) -> Vec2:
        return self._primitive.center

    @position.setter
    def position(self, value: Vec2):
        self._primitive.center = value

    def boundary(self) -> Rectangle:
        return Rectangle(
            self._primitive.center
            - Vec2(self._primitive.radius, self._primitive.radius),
            self._primitive.center
            + Vec2(self._primitive.radius, self._primitive.radius),
        )

    def collision(self, shape: ShapeProtocol) -> bool:
        return self.primitive.collision(shape.primitive)

    def penetration(self, shape: ShapeProtocol) -> Collision | None:
        return self.primitive.penetration(shape.primitive)

    def minkowski_difference(self, shape: ShapeProtocol) -> PrimitiveType:
        return self.primitive.minkowski_difference(shape.primitive)

    def __copy__(self) -> Self:
        return CircleShape(self._primitive.center, self._primitive.radius)


class PolygonShape:
    def __init__(self, *points: Vec2):
        if not points:
            raise ValueError("Polygon must have at least 1 point")
        self._primitive = Polygon(points)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(primitive: {self.primitive})"

    @property
    def primitive(self) -> Polygon:
        return self._primitive

    @property
    def position(self) -> Vec2:
        return self._primitive.center

    @position.setter
    def position(self, value: Vec2):
        self._primitive.center = value

    def boundary(self) -> Rectangle:
        return self._primitive.bounding_box

    def collision(self, shape: ShapeProtocol) -> bool:
        return self.primitive.collision(shape.primitive)

    def penetration(self, shape: ShapeProtocol) -> Collision | None:
        return self.primitive.penetration(shape.primitive)

    def minkowski_difference(self, shape: ShapeProtocol) -> PrimitiveType:
        return self.minkowski_difference(shape.primitive)

    def __copy__(self) -> Self:
        return PolygonShape(self.primitive.points)
