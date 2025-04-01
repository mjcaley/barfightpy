#pragma once

#include <variant>
#include <glm/vec2.hpp>
#include <bfphysics/primitives/Common.hpp>
#include <bfphysics/primitives/Circle.hpp>
#include <bfphysics/primitives/Rectangle.hpp>

namespace barfight::physics {
    class Shape {
        public:
        Shape(barfight::physics::primitives::Circle circle) : shape(circle) {}
        Shape(barfight::physics::primitives::Rectangle rectangle) : shape(rectangle) {}

        auto get_vec2_position() const -> glm::dvec2;
        auto set_vec2_position(const glm::dvec2& position) -> void;

        auto get_tuple_position() const -> std::tuple<double, double>;
        auto set_tuple_position(const std::tuple<double, double>& position) -> void;

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::primitives::FurthestError>;
        auto furthest(const std::tuple<double, double>& direction) const -> std::expected<std::tuple<double, double>, barfight::physics::primitives::FurthestError>;

        private:
        std::variant<barfight::physics::primitives::Circle, barfight::physics::primitives::Rectangle> shape;
    };
}
