#include <bfphysics/Collision.hpp>

auto barfight::physics::colliding(const Circle& c1, const Circle& c2) -> std::optional<collision> {
    auto distance = glm::distance(c1.center, c2.center);
    auto overlap = c1.radius + c2.radius - distance;

    if (overlap > 0) {
        auto normal = glm::normalize(c2.center - c1.center);
        auto resolution_vector = normal;
        return collision { normal, overlap };
    }

    return {};
}

auto barfight::physics::overlaps(const BoundingBox& b1, const BoundingBox& b2) -> bool {
    return b1.origin.x <= b2.origin.x + b2.size.x
        && b1.origin.x + b1.size.x >= b2.origin.x
        && b1.origin.y <= b2.origin.y + b2.size.y
        && b1.origin.y + b1.size.y >= b2.origin.y;
}
