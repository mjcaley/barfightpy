module;
#include <memory>
#include <vector>
#include <glm/vec2.hpp>

export module barfight.physics:QuadTreeNode;
import :BodyHandle;
import :BoundingBox;
import :QuadTree;

namespace barfight::physics {
    export class QuadTreeNode {
        public:
        QuadTreeNode(const glm::dvec2& origin, const glm::dvec2& size);
        ~QuadTreeNode();

        auto get_bounding_box() const -> BoundingBox;
        auto subdivide() -> void;
        auto clear() -> void;

        private:
        BoundingBox bounding_box { { 0.0, 0.0 }, { 0.0, 0.0 } };
        std::vector<BodyHandle> handles;
        std::unique_ptr<QuadTreeChildren> children;
    };
}

barfight::physics::QuadTreeNode::~QuadTreeNode() {}
