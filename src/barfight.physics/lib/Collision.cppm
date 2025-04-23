module;
#include <optional>

export module barfight.physics:Collision;
import glm;
import :BoundingBox;
import :Circle;
import :CollisionImpl;

namespace barfight::physics {
    export struct Collision {
        glm::dvec2 normal;
        double depth;
    };

    export auto colliding(const auto& shape1, const auto& shape2) -> std::optional<Collision> {
        return gjk(shape1, shape2)
            .transform([&](auto&& simplex) -> Collision {
                    EPAResult epa_collision = epa(shape1, shape2, simplex);
                    return Collision { epa_collision.normal, epa_collision.depth };
                }
            );
    }

    export auto colliding(const Circle& c1, const Circle& c2) -> std::optional<Collision> {
        auto distance = glm::distance(c1.center, c2.center);

        if (distance < c1.radius + c2.radius) {
            auto normal = glm::normalize(c2.center - c1.center);
            return Collision { normal, distance };
        }

        return {};
    }

    export auto overlaps(const BoundingBox& b1, const BoundingBox& b2) -> bool {
        return b1.origin.x <= b2.origin.x + b2.size.x
            && b1.origin.x + b1.size.x >= b2.origin.x
            && b1.origin.y <= b2.origin.y + b2.size.y
            && b1.origin.y + b1.size.y >= b2.origin.y;
    }

    export auto contains(const BoundingBox& parent, const BoundingBox& child) -> bool {
        return parent.origin.x <= child.origin.x
            && parent.origin.x + parent.size.x >= child.origin.x + child.size.x
            && parent.origin.y <= child.origin.y
            && parent.origin.y + parent.size.y >= child.origin.y + child.size.y;
    }

    export struct TimeOfImpact {
        double time;
        glm::dvec2 normal;
        double depth;
    };

    constexpr double epsilon = 1e-6;

    export auto time_of_impact(const auto& shape1, const auto& shape2, const glm::dvec2& velocity, double dt) -> std::optional<TimeOfImpact> {
        auto first_at_dest = shape1;
        first_at_dest.set_position(shape1.get_position() + velocity * dt);

        if (const auto early_collision = colliding(shape1, shape2)) {
            return TimeOfImpact { 0.0, early_collision->normal, early_collision->depth };
        }

        const auto late_hit = colliding(first_at_dest, shape2);
        if (!late_hit) {
            return {};
        }

        auto dt_min = 0.0;
        auto dt_mid = dt / 2.0;
        auto dt_max = dt;
        auto middle = shape1;

        while (dt_max - dt_min > epsilon) {
            dt_mid = dt_min + (dt_max - dt_min) / 2.0;
            middle.set_position(shape1.get_position() + velocity * dt_mid);

            if (const auto middle_hit = colliding(middle, shape2)) {
                dt_max = dt_mid;
            }
            else {
                dt_min = dt_mid;
            }
        }

        middle.set_position(shape1.get_position() + velocity * dt_mid);
        const auto middle_hit = colliding(middle, shape2);
        if (!middle_hit) { return {}; }
        return TimeOfImpact { dt_mid, middle_hit->normal, middle_hit->depth };
    }
}
