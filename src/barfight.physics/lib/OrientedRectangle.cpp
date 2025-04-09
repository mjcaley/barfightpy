#include <bfphysics/OrientedRectangle.hpp>

auto barfight::physics::OrientedRectangle::get_center() const -> glm::dvec2 {
    return center + half_size;
}

auto barfight::physics::OrientedRectangle::set_center(glm::dvec2 value) -> void {
    center = value;
}

auto barfight::physics::OrientedRectangle::get_vec2_position() const -> glm::dvec2 {
    return center;
}

auto barfight::physics::OrientedRectangle::set_vec2_position(glm::dvec2 position) -> void {
    center = position;
}

auto barfight::physics::OrientedRectangle::furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::FurthestError> {
    using barfight::physics::FurthestError;

    if (glm::dvec2 {0.0, 0.0} == direction) {
        return std::unexpected { FurthestError::ZERO_VECTOR };
    }

    if (direction.x <= 0 && direction.y <= 0) {
        return center - half_size;
    }
    else if (direction.x <= 0 && direction.y >= 0) {
        return center + glm::dvec2 { 0.0, -half_size.y };
    }
    else if (direction.x >= 0 && direction.y >= 0) {
        return center + half_size;
    }
    else {
        return center + glm::dvec2 { -half_size.x, 0.0 };
    }
}

auto barfight::physics::OrientedRectangle::get_tuple_center() const -> std::tuple<double, double> {
    return { center.x, center.y };
}

auto barfight::physics::OrientedRectangle::set_tuple_center(std::tuple<double, double> value) -> void {
    center = { std::get<0>(value), std::get<1>(value) };
}

auto barfight::physics::OrientedRectangle::get_tuple_half_size() const -> std::tuple<double, double> {
    return { half_size.x, half_size.y };
}

auto barfight::physics::OrientedRectangle::set_tuple_half_size(const std::tuple<double, double>& value) -> void {
    half_size = { std::get<0>(value), std::get<1>(value) };
}

auto barfight::physics::OrientedRectangle::get_tuple_position() const -> std::tuple<double, double> {
    auto position = get_vec2_position();

    return { position.x, position.y };
}

auto barfight::physics::OrientedRectangle::set_tuple_position(const std::tuple<double, double>& position) -> void {
    set_vec2_position({ std::get<0>(position), std::get<1>(position) });
}
