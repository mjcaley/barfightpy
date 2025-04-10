module;
#include <expected>
#include <optional>
#include <tuple>
#include <variant>
#include <glm/vec2.hpp>

export module barfight.physics:Shape;
import :BoundingBox;
import :PrimitiveCommon;
import :Circle;
import :OrientedRectangle;
import :Polygon;
import :Rectangle;

namespace barfight::physics {
    auto colliding_visitor = [](const auto& shape1, const auto& shape2) -> std::optional<barfight::physics::collision> {
        return barfight::physics::colliding(shape1, shape2);
    };

    export class Shape {
        public:
        Shape(barfight::physics::Circle circle) : shape(circle) {}
        Shape(barfight::physics::OrientedRectangle rectangle) : shape(rectangle) {}
        Shape(barfight::physics::Polygon polygon) : shape(polygon) {}
        Shape(barfight::physics::Rectangle rectangle) : shape(rectangle) {}
        Shape(std::variant<barfight::physics::Circle, barfight::physics::OrientedRectangle, barfight::physics::Polygon, barfight::physics::Rectangle> shape) : shape(shape) {}

        auto get_vec2_position() const -> glm::dvec2 {
            return std::visit([](auto& s) { return s.get_vec2_position(); }, shape);
        }

        auto set_vec2_position(const glm::dvec2& position) -> void {
            std::visit([position](auto& s) { s.set_vec2_position(position); }, shape);
        }

        auto get_tuple_position() const -> std::tuple<double, double> {
            return std::visit([](const auto& shape) { return shape.get_tuple_position(); }, shape);
        }

        auto set_tuple_position(const std::tuple<double, double>& position) -> void {
            std::visit([position](auto& shape) { shape.set_tuple_position(position); }, shape);
        }

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::FurthestError> {
            return std::visit([direction](const auto& shape) { return shape.furthest(direction); }, shape);
        }

        auto furthest(const std::tuple<double, double>& direction) const -> std::expected<std::tuple<double, double>, barfight::physics::FurthestError> {
            return furthest(glm::dvec2 {std::get<0>(direction), std::get<1>(direction)})
                .transform([](auto p) { return std::make_tuple(p.x, p.y); });
        }

        auto get_bounding_box() const -> BoundingBox {
            return std::visit([](const auto& shape) { return shape.get_bounding_box(); }, shape);
        }

        auto get_shape() const -> const std::variant<barfight::physics::Circle, barfight::physics::OrientedRectangle, barfight::physics::Polygon, barfight::physics::Rectangle>& {
            return shape;
        }

        auto colliding(const Shape& other) const -> std::optional<collision> {
            return std::visit(colliding_visitor, shape, other.shape);
        }

        private:
        std::variant<barfight::physics::Circle, barfight::physics::OrientedRectangle, barfight::physics::Polygon, barfight::physics::Rectangle> shape;
    };
}
