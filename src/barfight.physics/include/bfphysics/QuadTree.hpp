#pragma once

#include <bfphysics/BodyHandle.hpp>
#include <bfphysics/BoundingBox.hpp>
#include <memory>
#include <vector>
#include <glm/vec2.hpp>

namespace barfight::physics {
    struct QuadTreeChildren;

    class QuadTreeNode {
        public:
        QuadTreeNode(const glm::dvec2& origin, const glm::dvec2& size)
            : _bounding_box(BoundingBox { origin, size }) {}
        ~QuadTreeNode();

        auto bounding_box() const -> BoundingBox;
        auto subdivide() -> void;
        auto clear() -> void;

        private:
        BoundingBox _bounding_box;
        std::vector<BodyHandle> handles;
        std::unique_ptr<QuadTreeChildren> children;
    };

    struct QuadTreeChildren {
        QuadTreeChildren(const glm::dvec2& origin, const glm::dvec2& size) {}
        // QuadTreeChildren(const glm::dvec2& origin, const glm::dvec2& size) :
        //     bottom_left({ origin, size / 2.0 }),
        //     top_left({ glm::dvec2 { origin.x, origin.y + size.y / 2.0 }, size / 2.0 }),
        //     top_right({ origin + size / 2.0, size / 2.0 }),
        //     bottom_right({ glm::dvec2 { origin.x + size.x / 2.0, origin.y }, size / 2.0 })
        //     {}

        // QuadTreeNode bottom_left;
        // QuadTreeNode top_left;
        // QuadTreeNode top_right;
        // QuadTreeNode bottom_right;
    };
}
