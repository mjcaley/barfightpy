module;
#include <memory>
#include <vector>
#include <glm/vec2.hpp>

export module barfight.physics:QuadTreeNode;
import :QuadTreeFwd;
import :BodyHandle;
import :BoundingBox;

namespace barfight::physics {
    export class QuadTreeNode {
        public:
        QuadTreeNode(const glm::dvec2& origin, const glm::dvec2& size) : origin(origin), size(size) {}
        ~QuadTreeNode();

        auto get_bounding_box() const -> BoundingBox {
            return BoundingBox { origin, size };
        }

        auto subdivide() -> void;
        auto clear() -> void {
            handles.clear();
            top_left.reset();
            top_right.reset();
            bottom_left.reset();
            bottom_right.reset();
        }

        private:
        glm::dvec2 origin;
        glm::dvec2 size;
        std::vector<BodyHandle> handles;
        
        std::unique_ptr<QuadTreeNode> top_left;
        std::unique_ptr<QuadTreeNode> top_right;
        std::unique_ptr<QuadTreeNode> bottom_left;
        std::unique_ptr<QuadTreeNode> bottom_right;
    };
}
