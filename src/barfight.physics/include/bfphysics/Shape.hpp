#pragma once

#include <variant>
#include <glm/vec2.hpp>
#include <bfphysics/PrimitiveCommon.hpp>
#include <bfphysics/Circle.hpp>
#include <bfphysics/OrientedRectangle.hpp>
#include <bfphysics/Polygon.hpp>
#include <bfphysics/Rectangle.hpp>
#include <bfphysics/Collision.hpp>

namespace barfight::physics {
    class Shape {
        public:
        Shape(barfight::physics::Circle circle) : shape(circle) {}
        Shape(barfight::physics::OrientedRectangle rectangle) : shape(rectangle) {}
        Shape(barfight::physics::Polygon polygon) : shape(polygon) {}
        Shape(barfight::physics::Rectangle rectangle) : shape(rectangle) {}
        Shape(std::variant<barfight::physics::Circle, barfight::physics::OrientedRectangle, barfight::physics::Polygon, barfight::physics::Rectangle> shape) : shape(shape) {}

        auto get_vec2_position() const -> glm::dvec2;
        auto set_vec2_position(const glm::dvec2& position) -> void;

        auto get_tuple_position() const -> std::tuple<double, double>;
        auto set_tuple_position(const std::tuple<double, double>& position) -> void;

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::FurthestError>;
        auto furthest(const std::tuple<double, double>& direction) const -> std::expected<std::tuple<double, double>, barfight::physics::FurthestError>;

        auto get_bounding_box() const -> BoundingBox;
        auto get_shape() const -> const std::variant<barfight::physics::Circle, barfight::physics::OrientedRectangle, barfight::physics::Polygon, barfight::physics::Rectangle>&;

        auto colliding(const Shape& other) const -> std::optional<collision>;

        private:
        std::variant<barfight::physics::Circle, barfight::physics::OrientedRectangle, barfight::physics::Polygon, barfight::physics::Rectangle> shape;
    };
}
