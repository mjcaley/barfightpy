#include <expected>
#include "bfphysics/primitives/Circle.hpp"
#include <glm/glm.hpp>

auto barfight::physics::primitives::Circle::get_position() const -> glm::dvec2 {
    return center;
}

auto barfight::physics::primitives::Circle::set_position(glm::bvec2 position) {
    center = position;
}

auto barfight::physics::primitives::Circle::furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::primitives::FurthestError> {
    using barfight::physics::primitives::FurthestError;
    
    if (glm::dvec2 {0.0, 0.0} == direction) {
        return std::unexpected { FurthestError::ZERO_VECTOR };
    }

    return center + radius * glm::normalize(direction);
}
