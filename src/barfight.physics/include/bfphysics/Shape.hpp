#pragma once

#include <variant>
#include <glm/vec2.hpp>
#include <bfphysics/PrimitiveCommon.hpp>
#include <bfphysics/Circle.hpp>
#include <bfphysics/Rectangle.hpp>

namespace barfight::physics {
    class Shape {
        public:
        Shape(barfight::physics::Circle circle) : shape(circle) {}
        Shape(barfight::physics::Rectangle rectangle) : shape(rectangle) {}

        auto get_vec2_position() const -> glm::dvec2;
        auto set_vec2_position(const glm::dvec2& position) -> void;

        auto get_tuple_position() const -> std::tuple<double, double>;
        auto set_tuple_position(const std::tuple<double, double>& position) -> void;

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::FurthestError>;
        auto furthest(const std::tuple<double, double>& direction) const -> std::expected<std::tuple<double, double>, barfight::physics::FurthestError>;

        private:
        std::variant<barfight::physics::Circle, barfight::physics::Rectangle> shape;
    };
}
