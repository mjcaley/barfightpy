#pragma once

#include <variant>
#include <glm/vec2.hpp>
#include <bfphysics/primitives/Circle.hpp>

namespace barfight::physics {
    class Shape {
        public:
        Shape(barfight::physics::primitives::Circle circle) : shape(circle) {}

        auto get_vec2_position() const -> glm::dvec2;
        auto set_vec2_position(const glm::dvec2& position);
        auto furthest_vec2(const glm::dvec2& direction) const -> glm::dvec2;

        auto get_tuple_position() const -> std::tuple<double, double>;
        auto set_tuple_position(const std::tuple<double, double>& position);
        auto furthest_tuple(const std::tuple<double, double>& direction) -> std::tuple<double, double>;

        private:
        std::variant<barfight::physics::primitives::Circle> shape;
    };
}
