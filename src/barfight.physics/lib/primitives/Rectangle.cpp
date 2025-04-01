#include <expected>
#include "bfphysics/primitives/Rectangle.hpp"
#include <glm/glm.hpp>

auto barfight::physics::primitives::Rectangle::get_vec2_position() const -> glm::dvec2 {
    return origin + (size / 2.0);
}

auto barfight::physics::primitives::Rectangle::set_vec2_position(glm::dvec2 position) -> void {
    origin = position - (size / 2.0);
}

auto barfight::physics::primitives::Rectangle::furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::primitives::FurthestError> {
    using barfight::physics::primitives::FurthestError;

    if (glm::dvec2 {0.0, 0.0} == direction) {
        return std::unexpected { FurthestError::ZERO_VECTOR };
    }

    if (direction.x <= 0 && direction.y <= 0) {
        return origin;
    }
    else if (direction.x <= 0 && direction.y >= 0) {
        return glm::dvec2 { origin.x, origin.y + size.y };
    }
    else if (direction.x >=0 && direction.y >= 0) {
        return origin + size;
    }
    else {
        return glm::dvec2 { origin.x + size.x, origin.y };
    }
}

auto barfight::physics::primitives::Rectangle::get_tuple_origin() const -> std::tuple<double, double> {
    return { origin.x, origin.y };
}

auto barfight::physics::primitives::Rectangle::set_tuple_origin(std::tuple<double, double> value) -> void {
    origin = { std::get<0>(value), std::get<1>(value) };
}

auto barfight::physics::primitives::Rectangle::get_tuple_size() const -> std::tuple<double, double> {
    return { size.x, size.y };
}

auto barfight::physics::primitives::Rectangle::set_tuple_size(const std::tuple<double, double>& value) -> void {
    size = { std::get<0>(value), std::get<1>(value) };
}

auto barfight::physics::primitives::Rectangle::get_tuple_position() const -> std::tuple<double, double> {
    auto position = get_vec2_position();

    return { position.x, position.y };
}

auto barfight::physics::primitives::Rectangle::set_tuple_position(const std::tuple<double, double>& position) -> void {
    set_vec2_position({ std::get<0>(position), std::get<1>(position) });
}
