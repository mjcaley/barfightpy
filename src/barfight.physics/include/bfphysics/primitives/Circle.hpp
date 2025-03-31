#pragma once

#include <expected>
#include <bfphysics/primitives/Common.hpp>
#include <glm/vec2.hpp>

namespace barfight::physics::primitives {
    struct Circle {
        glm::dvec2 center;
        double radius;

        auto get_position() const -> glm::dvec2;
        auto set_position(glm::bvec2 position);
        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::primitives::FurthestError>;
    };
}
