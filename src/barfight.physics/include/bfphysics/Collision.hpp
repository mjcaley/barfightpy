#pragma once

#include <bfphysics/Circle.hpp>
#include <glm/glm.hpp>
#include <bfphysics/Collision.impl.hpp>

namespace barfight::physics {
    using barfight::physics::Circle;

    using collision = impl::collision;

    auto resolution(auto shape1, auto shape2) -> std::optional<collision> {
        return {};
    }

    auto colliding(const auto& shape1, const auto& shape2) -> std::optional<collision> {
        return impl::gjk(shape1, shape2)
            .transform([&](auto&& simplex) -> collision {
                return { impl::epa(shape1, shape2, simplex) };
            });
    }

    auto colliding(const Circle& c1, const Circle& c2) -> std::optional<collision> {
        auto distance = glm::distance(c1.center, c2.center);
        auto overlap = c1.radius + c2.radius - distance;

        if (overlap > 0) {
            auto normal = glm::normalize(c2.center - c1.center);
            auto resolution_vector = normal;
            return collision { normal, overlap };
        }

        return {};
    }
}
