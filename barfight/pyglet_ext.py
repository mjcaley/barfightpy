from pyglet.math import Vec2


def _rotate90(self) -> Vec2:
    return Vec2(-self.y, self.x)


def _rotate180(self) -> Vec2:
    return Vec2(-self.x, -self.y)


def _cross(self, v: Vec2) -> float:
    return self.x * v.y - self.y * v.x


Vec2.rotate90 = _rotate90
Vec2.rotate180 = _rotate180
Vec2.cross = _cross
