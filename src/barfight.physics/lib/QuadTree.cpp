#include <bfphysics/QuadTree.hpp>

barfight::physics::QuadTreeNode::~QuadTreeNode() {}

auto barfight::physics::QuadTreeNode::bounding_box() const -> BoundingBox {
    return _bounding_box;
}

auto barfight::physics::QuadTreeNode::subdivide() -> void {
    children = std::make_unique<QuadTreeChildren>(_bounding_box.origin, _bounding_box.size);
}

auto barfight::physics::QuadTreeNode::clear() -> void {
    handles.clear();
    children.reset();
}