module;
#include <optional>
#include <glm/glm.hpp>

export module barfight.physics:Collision;
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
                    epa_result epa_collision = epa(shape1, shape2, simplex);
                    return Collision { epa_collision.normal, epa_collision.depth };
                }
            );
    }

    export auto colliding(const Circle& c1, const Circle& c2) -> std::optional<Collision> {
        auto distance = glm::distance(c1.center, c2.center);
        auto overlap = c1.radius + c2.radius - distance;

        if (overlap > 0) {
            auto normal = glm::normalize(c2.center - c1.center);
            auto resolution_vector = normal;
            return Collision { normal, overlap };
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
}
