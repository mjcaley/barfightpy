#include <bfphysics/Collision.hpp>
#include <bfphysics/Shape.hpp>
#include <expected>
#include <tuple>
#include <variant>
#include <glm/vec2.hpp>

auto barfight::physics::Shape::get_vec2_position() const -> glm::dvec2 {
    return std::visit([](auto& s) { return s.get_vec2_position(); }, shape);
}

auto barfight::physics::Shape::set_vec2_position(const glm::dvec2& position) -> void {
    std::visit([position](auto& s) { s.set_vec2_position(position); }, shape);
}

auto barfight::physics::Shape::furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::FurthestError> {
    return std::visit([direction](const auto& shape) { return shape.furthest(direction); }, shape);
}

auto barfight::physics::Shape::get_tuple_position() const -> std::tuple<double, double> {
    return std::visit([](const auto& shape) { return shape.get_tuple_position(); }, shape);
}

auto barfight::physics::Shape::set_tuple_position(const std::tuple<double, double>& position) -> void {
    std::visit([position](auto& shape) { shape.set_tuple_position(position); }, shape);
}

auto barfight::physics::Shape::furthest(const std::tuple<double, double>& direction) const -> std::expected<std::tuple<double, double>, barfight::physics::FurthestError> {
    return furthest(glm::dvec2 {std::get<0>(direction), std::get<1>(direction)})
        .transform([](auto p) { return std::make_tuple(p.x, p.y); });
}

auto barfight::physics::Shape::get_bounding_box() const -> BoundingBox {
    return std::visit([](const auto& shape) { return shape.get_bounding_box(); }, shape);
}

auto barfight::physics::Shape::get_shape() const -> const std::variant<barfight::physics::Circle, barfight::physics::OrientedRectangle, barfight::physics::Polygon, barfight::physics::Rectangle>& {
    return shape;
}

auto colliding_visitor = [](const auto& shape1, const auto& shape2) -> std::optional<barfight::physics::collision> {
    return barfight::physics::colliding(shape1, shape2);
};

auto barfight::physics::Shape::colliding(const Shape& other) const -> std::optional<collision> {
    return std::visit(colliding_visitor, shape, other.shape);
}
