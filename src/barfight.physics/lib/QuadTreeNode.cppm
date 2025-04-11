module;
#include <memory>
#include <optional>
#include <set>
#include <vector>
#include <glm/vec2.hpp>

export module barfight.physics:QuadTreeNode;
import :QuadTreeFwd;
import :Body;
import :BodyHandle;
import :BoundingBox;
import :Collision;

namespace barfight::physics {
    export class QuadTreeNode {
        public:
        QuadTreeNode(const glm::dvec2& origin, const glm::dvec2& size, const std::vector<std::optional<Body>>& bodies, int depth = 8, int limit = 32)
            : origin(origin), size(size), bodies(bodies), depth(depth), limit(limit) {}
        ~QuadTreeNode();

        auto get_bounding_box() const -> BoundingBox {
            return BoundingBox { origin, size };
        }

        auto add(const BodyHandle handle) -> bool {
            const auto& body = bodies[handle.get_id()];
            if (!body) { return false; }

            if (fits(handle)) {
                if (top_left->add(handle)) { return true; }
                if (top_right->add(handle)) { return true; }
                if (bottom_left->add(handle)) { return true; }
                if (bottom_left->add(handle)) { return true; }

                handles.insert(handle);
                return true;
            }

            return false;
        }

        auto remove(const BodyHandle handle) -> void {
            handles.erase(handle);
            if (top_left) { top_left->remove(handle); }
            if (top_right) { top_right->remove(handle); }
            if (bottom_left) { bottom_left->remove(handle); }
            if (bottom_right) { bottom_right->remove(handle); }
        }

        auto query(const BoundingBox& target) const -> std::set<BodyHandle> {
            std::set<BodyHandle> found {};

            for (const auto child_handle : handles) {
                
            }

            return found;
        }

        auto is_subdivided() const -> bool {
            return top_left && top_right && bottom_left && bottom_right;
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
        int limit;
        int depth;
        const std::vector<std::optional<Body>>& bodies;
        std::set<BodyHandle> handles;
        
        std::unique_ptr<QuadTreeNode> top_left;
        std::unique_ptr<QuadTreeNode> top_right;
        std::unique_ptr<QuadTreeNode> bottom_left;
        std::unique_ptr<QuadTreeNode> bottom_right;

        // auto overlaps(const auto& BodyHandle b1, const auto BodyHandle b2) const -> bool {
        //     const auto body1 = bodies[b1];
        //     const auto body2 = bodies[b2];

        //     if (!body1 && !body2) { return false; }

        //     return overlaps(body1->shape.get_bounding_box(), body2->shape.get_bounding_box());
        // }

        auto fits(const auto BodyHandle handle) const -> bool {
            const auto& body = bodies[handle.get_id()];
            if (!body) { return false; }

            return contains(get_bounding_box(), body->shape.get_bounding_box());
        }
    };
}
