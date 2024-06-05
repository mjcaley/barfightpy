from pyglet.math import Vec2
from barfight.physics import Body, QuadNode, QuadTree, Rectangle


def test_quadnode_insert_not_in_boundary():
    q = QuadNode(Rectangle(Vec2(0, 0), Vec2(1, 1)), 10)
    result = q.insert(Body(Rectangle(Vec2(10, 10), Vec2(11, 11))))

    assert result is False
    

def test_quadnode_inserts_in_boundary():
    q = QuadNode(Rectangle(Vec2(0, 0), Vec2(10, 10)), 10)
    result = q.insert(Body(Rectangle(Vec2(2.5, 2.5), Vec2(7.5, 7.5))))

    assert result is True


def test_quadnode_subdivide():
    q = QuadNode(Rectangle(Vec2(0, 0), Vec2(100, 100)), 10)
    q.subdivide()

    assert q.is_divided is True
    assert Rectangle(Vec2(0, 0), Vec2(50, 50)) == q.bottom_left.boundary
    assert Rectangle(Vec2(50, 0), Vec2(100, 50)) == q.bottom_right.boundary
    assert Rectangle(Vec2(0, 50), Vec2(50, 100)) == q.top_left.boundary
    assert Rectangle(Vec2(50, 50), Vec2(100, 100)) == q.top_right.boundary
