#pragma once

#include <bfphysics/BoundingBox.hpp>
#include <bfphysics/Circle.hpp>
#include <glm/glm.hpp>
#include <bfphysics/Collision.impl.hpp>

namespace barfight::physics {
    using barfight::physics::BoundingBox;
    using barfight::physics::Circle;

    struct collision {
        glm::dvec2 normal;
        double depth;
    };

    auto colliding(const auto& shape1, const auto& shape2) -> std::optional<collision> {
        return impl::gjk(shape1, shape2)
            .transform([&](auto&& simplex) -> collision {
                    impl::epa_result epa_collision = impl::epa(shape1, shape2, simplex);
                    return collision { epa_collision.normal, epa_collision.depth };
                }
            );
    }

    auto colliding(const Circle& c1, const Circle& c2) -> std::optional<collision>;

    auto overlaps(const BoundingBox& b1, const BoundingBox& b2) -> bool;
}
