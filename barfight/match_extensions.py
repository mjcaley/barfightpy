from pyglet.math import Vec2


def patch_vec2():
    Vec2.__match_args__ = ("x", "y")
