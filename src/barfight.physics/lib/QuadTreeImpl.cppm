module;
#include <memory>

module barfight.physics:QuadTreeImpl;
import glm;
import :QuadTreeNode;

namespace barfight::physics {
    QuadTreeNode::~QuadTreeNode() {}
    
    auto QuadTreeNode::subdivide() -> void {
        auto next_depth = std::max(depth, depth - 1);

        bottom_left = std::make_unique<QuadTreeNode>(origin, size / 2.0, bodies, next_depth);
        top_left = std::make_unique<QuadTreeNode>(glm::dvec2 { origin.x, origin.y + size.y / 2.0 }, size / 2.0, bodies, next_depth);
        top_right = std::make_unique<QuadTreeNode>(origin + size / 2.0, size / 2.0, bodies, next_depth);
        bottom_right = std::make_unique<QuadTreeNode>(glm::dvec2 { origin.x + size.x / 2.0, origin.y }, size / 2.0, bodies, next_depth);
    }
}
