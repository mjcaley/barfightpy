module;
#include <memory>
#include <optional>
#include <unordered_set>
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
        QuadTreeNode(const glm::dvec2& origin, const glm::dvec2& size, std::vector<std::optional<Body>>& bodies, int depth = 8, int limit = 32)
            : origin(origin), size(size), bodies(bodies), depth(depth), limit(limit) {}
        QuadTreeNode(QuadTreeNode&& other) = default;
        ~QuadTreeNode();

        auto operator=(QuadTreeNode&& other) -> QuadTreeNode& {
            if (this != &other) {
                origin = other.origin;
                size = other.size;
                limit = other.limit;
                depth = other.depth;
                bodies = other.bodies;
                handles = std::move(other.handles);
                top_left = std::move(other.top_left);
                top_right = std::move(other.top_right);
                bottom_left = std::move(other.bottom_left);
                bottom_right = std::move(other.bottom_right);
            }

            return *this;
        }

        auto operator=(const QuadTreeNode& other) -> QuadTreeNode& = delete;

        auto get_bounding_box() const -> BoundingBox {
            return BoundingBox { origin, size };
        }

        auto fits(const BodyHandle handle) const -> bool {
            const auto& body = bodies[handle.get_id()];
            if (!body) { return false; }

            return contains(get_bounding_box(), body->shape.get_bounding_box());
        }

        auto add(const BodyHandle handle) -> bool {
            const auto& body = bodies[handle.get_id()];
            if (!body) { return false; }

            if (fits(handle)) {
                if (!is_subdivided()) {
                    handles.insert(handle);
                    return true;
                }

                if (top_left->add(handle)) { return true; }
                if (top_right->add(handle)) { return true; }
                if (bottom_left->add(handle)) { return true; }
                if (bottom_left->add(handle)) { return true; }
            }

            return false;
        }

        auto remove(const BodyHandle handle) -> void {
            handles.erase(handle);
            if (!is_subdivided()) { return; }
            top_left->remove(handle);
            top_right->remove(handle);
            bottom_left->remove(handle);
            bottom_right->remove(handle);
        }

        auto query(const BoundingBox& target) const -> std::unordered_set<BodyHandle> {
            std::unordered_set<BodyHandle> found {};

            if (!overlaps(target, get_bounding_box())) { return found; }

            for (const auto child_handle : handles) {
                const auto& body = bodies[child_handle.get_id()];
                if (!body) { continue; }

                if (overlaps(target, body->shape.get_bounding_box())) {
                    found.insert(child_handle);
                }
            }

            if (!is_subdivided()) { return found; }
            found.merge(top_left->query(target));
            found.merge(top_right->query(target));
            found.merge(bottom_left->query(target));
            found.merge(bottom_right->query(target));

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
        std::vector<std::optional<Body>>& bodies;
        std::unordered_set<BodyHandle> handles;

        std::unique_ptr<QuadTreeNode> top_left;
        std::unique_ptr<QuadTreeNode> top_right;
        std::unique_ptr<QuadTreeNode> bottom_left;
        std::unique_ptr<QuadTreeNode> bottom_right;
    };
}
