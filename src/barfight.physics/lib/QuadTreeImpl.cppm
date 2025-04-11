module;
#include <memory>
#include <glm/vec2.hpp>

module barfight.physics:QuadTreeImpl;
import :QuadTreeNode;

namespace barfight::physics {
    QuadTreeNode::~QuadTreeNode() {}
    
    auto QuadTreeNode::subdivide() -> void {
        bottom_left = std::make_unique<QuadTreeNode>(origin, size / 2.0);
        top_left = std::make_unique<QuadTreeNode>(glm::dvec2 { origin.x, origin.y + size.y / 2.0 }, size / 2.0);
        top_right = std::make_unique<QuadTreeNode>(origin + size / 2.0, size / 2.0);
        bottom_right = std::make_unique<QuadTreeNode>(glm::dvec2 { origin.x + size.x / 2.0, origin.y }, size / 2.0);
    }
}
