#pragma once

#include <variant>
#include <glm/vec2.hpp>
#include <bfphysics/primitives/Circle.hpp>

namespace barfight::physics {
    class Shape {
        public:
        Shape(barfight::physics::primitives::Circle circle) : shape(circle) {}
        
        auto get_position() const -> glm::bvec2;
        auto set_position(const glm::bvec2& position);
        auto furthest(glm::dvec2 direction) const -> glm::bvec2;

        private:
        std::variant<barfight::physics::primitives::Circle> shape;
    };
}
