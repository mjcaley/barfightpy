#include <expected>
#include "bfphysics/Circle.hpp"
#include <glm/glm.hpp>


auto barfight::physics::Circle::get_center() const -> glm::dvec2 {
    return center;
}

auto barfight::physics::Circle::set_center(glm::dvec2 value) -> void {
    center = value;
}

auto barfight::physics::Circle::get_tuple_center() const -> std::tuple<double, double> {
    return { center.x, center.y };
}

auto barfight::physics::Circle::set_tuple_center(std::tuple<double, double> position) -> void {
    center = { std::get<0>(position), std::get<1>(position) };
}

auto barfight::physics::Circle::get_vec2_position() const -> glm::dvec2 {
    return center;
}

auto barfight::physics::Circle::set_vec2_position(glm::dvec2 position) -> void {
    center = position;
}

auto barfight::physics::Circle::furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::FurthestError> {
    using barfight::physics::FurthestError;

    if (glm::dvec2 {0.0, 0.0} == direction) {
        return std::unexpected { FurthestError::ZERO_VECTOR };
    }

    return center + radius * glm::normalize(direction);
}

auto barfight::physics::Circle::get_tuple_position() const -> std::tuple<double, double> {
    auto position = get_vec2_position();

    return std::make_tuple(position.x, position.y);
}

auto barfight::physics::Circle::set_tuple_position(const std::tuple<double, double>& position) -> void {
    set_vec2_position(glm::dvec2 { std::get<0>(position), std::get<1>(position) });
}
