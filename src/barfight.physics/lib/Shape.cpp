#include <bfphysics/Shape.hpp>
#include <expected>
#include <tuple>
#include <glm/vec2.hpp>

auto barfight::physics::Shape::get_vec2_position() const -> glm::dvec2 {
    return std::visit([](auto& s) { return s.get_position(); }, shape);
}

auto barfight::physics::Shape::set_vec2_position(const glm::dvec2& position) {
    std::visit([position](auto& s) { s.set_position(position); }, shape);
}

auto barfight::physics::Shape::furthest_vec2(const glm::dvec2& direction) const -> glm::dvec2 {
    return std::visit([shape, direction]() { return shape.furthest(direction); });
}

auto barfight::physics::Shape::get_tuple_position() const -> std::tuple<double, double> {
    auto position = get_vec2_position();

    return std::make_tuple(position.x, position.y);
}

auto barfight::physics::Shape::set_tuple_position(const std::tuple<double, double>& position) {
    set_vec2_position(glm::dvec2 { std::get<0>(position), std::get<1>(position) });
}

auto barfight::physics::Shape::furthest_tuple(const std::tuple<double, double>& direction) const -> std::tuple<double, double> {
    auto point = furthest_vec2(glm::dvec2 { std::get<0>(direction), std::get<1>(direction) });

    return std::make_tuple(point.x, point.y);
}
