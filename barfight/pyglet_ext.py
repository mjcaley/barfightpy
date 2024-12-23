from pyglet.math import Vec2


def _rotate90(self) -> Vec2:
    return Vec2(-self.y, self.x)


def _rotate180(self) -> Vec2:
    return Vec2(-self.x, -self.y)


Vec2.rotate90 = _rotate90
Vec2.rotate180 = _rotate180
