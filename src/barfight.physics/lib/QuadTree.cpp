#include <bfphysics/QuadTree.hpp>
#include <bfphysics/BoundingBox.hpp>

barfight::physics::QuadTreeNode::QuadTreeNode(const glm::dvec2& origin, const glm::dvec2& size) {
    bounding_box = BoundingBox { origin, size };
}

barfight::physics::QuadTreeNode::~QuadTreeNode() {}

auto barfight::physics::QuadTreeNode::get_bounding_box() const -> BoundingBox {
    return bounding_box;
}

auto barfight::physics::QuadTreeNode::subdivide() -> void {
    children = std::make_unique<QuadTreeChildren>(bounding_box.origin, bounding_box.size);
}

auto barfight::physics::QuadTreeNode::clear() -> void {
    handles.clear();
    children.reset();
}
