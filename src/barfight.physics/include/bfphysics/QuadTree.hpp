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

    struct QuadTreeChildren {
        QuadTreeChildren(const glm::dvec2& origin, const glm::dvec2& size) :
            bottom_left(QuadTreeNode { origin, size / 2.0 }),
            top_left(QuadTreeNode { glm::dvec2 { origin.x, origin.y + size.y / 2.0 }, size / 2.0 }),
            top_right(QuadTreeNode { origin + size / 2.0, size / 2.0 }),
            bottom_right(QuadTreeNode { glm::dvec2 { origin.x + size.x / 2.0, origin.y }, size / 2.0 })
            {}

        QuadTreeNode bottom_left;
        QuadTreeNode top_left;
        QuadTreeNode top_right;
        QuadTreeNode bottom_right;
    };
}
