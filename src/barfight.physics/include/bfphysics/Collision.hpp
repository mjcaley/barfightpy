#include <optional>
#include <bfphysics/primitives/Circle.hpp>
#include <glm/glm.hpp>

namespace barfight::physics {
    using barfight::physics::primitives::Circle;

    struct collision {
        glm::dvec2 normal;
        double depth;
    };

    auto resolution(auto shape1, auto shape2) -> std::optional<collision> {
        return {};
    }

    auto triple_product(glm::dvec2 a, glm::dvec2 b, glm::dvec2 c) -> glm::dvec2 {
        auto z = a.x * b.y - a.y * b.x;

        return { -c.y * z, c.x * z};
    }

    // auto support(std::vector<glm::dvec2> vertices, glm::dvec2 direction) -> glm::dvec2 {
    //     auto furthest = std::ranges::max_element(
    //         vertices,
    //         [&direction](const auto& v1, const auto& v2) {
    //             return glm::dot(v1, direction) < glm::dot(v2, direction);
    //         });

    //     return *furthest;
    // }

    auto support(const auto& shape1, const auto& shape2, const glm::dvec2& direction) -> glm::dvec2 {
        return shape1.furthest(direction) - shape2.furthest(-direction);
    }

    auto colliding(const auto& shape1, const auto& shape2) -> std::optional<collision> {
        return {};
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
