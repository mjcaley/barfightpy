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
        super().__init__(Point(point))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(point={self.primitive.point})"

    def boundary(self) -> Rectangle:
        return Rectangle(self.primitive.point, Vec2())


class RectangleShape(Shape):
    def __init__(self, origin: Vec2 | None = None, size: Vec2 | None = None):
        origin = origin or Vec2()
        size = size or Vec2()
        super().__init__(Rectangle(origin, size))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(primitive: {self.primitive})"

    def boundary(self) -> Rectangle:
        return self.primitive

    def __copy__(self) -> Self:
        return RectangleShape(self.primitive.origin, self.primitive.size)


class OrientedRectangleShape(Shape):
    def __init__(
        self, center: Vec2 | None = None, half_extent: Vec2 | None = None, rotation: float = 0
    ):
        center = center or Vec2()
        half_extent = half_extent or Vec2()
        super().__init__(OrientedRectangle(center, half_extent, rotation))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(center={self.primitive.center}, half_extent={self.primitive.half_extent}, rotation={self.primitive.rotation})"

    def boundary(self) -> Rectangle:
        min_x = inf
        max_x = -inf
        min_y = inf
        max_y = -inf

        for vertex in self.primitive.vertices():
            min_x = min(min_x, vertex.x)
            max_x = max(max_x, vertex.x)
            min_y = min(min_y, vertex.y)
            max_y = max(max_y, vertex.y)

        return Rectangle(Vec2(min_x, min_y), Vec2(max_x - min_x, max_y - min_y))

    def __copy__(self) -> Self:
        return OrientedRectangleShape(
            self._primitive.center,
            self._primitive.half_extent,
            self._primitive.rotation,
        )


class CircleShape(Shape):
    def __init__(self, center: Vec2 | None = None, radius: float = 0):
        center = center or Vec2()
        super().__init__(Circle(center, radius))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(center={self.primitive.center}, radius={self.primitive.radius})"

    def boundary(self) -> Rectangle:
        return Rectangle(
            self._primitive.center
            - Vec2(self.primitive.radius, self.primitive.radius),
            self._primitive.center
            + Vec2(self.primitive.radius, self.primitive.radius),
        )

    def __copy__(self) -> Self:
        return CircleShape(self._primitive.center, self._primitive.radius)


class PolygonShape(Shape):
    def __init__(self, *points: Vec2):
        if not points:
            raise ValueError("Polygon must have at least 1 point")
        super().__init__(Polygon(points))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(*points={self.primitive.points})"

    def boundary(self) -> Rectangle:
        return self._primitive.bounding_box

    def __copy__(self) -> Self:
        return PolygonShape(self.primitive.points)
