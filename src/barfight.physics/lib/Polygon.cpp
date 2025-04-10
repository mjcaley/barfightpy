#include <bfphysics/BoundingBox.hpp>
#include <bfphysics/Polygon.hpp>
#include <algorithm>
#include <limits>
#include <ranges>
#include <tuple>
#include <glm/glm.hpp>

auto barfight::physics::Polygon::get_tuple_points() const -> std::vector<std::tuple<double, double>> {
    std::vector<std::tuple<double, double>> tuple_points;
    std::ranges::copy(
        points | std::views::transform(
            [](const auto& point) { return std::make_tuple(point.x, point.y); }
        ),
        std::back_inserter(tuple_points)
    );

    return tuple_points;
}

auto barfight::physics::Polygon::set_tuple_points(const std::vector<std::tuple<double, double>>& value) -> void {
    points.clear();
    std::ranges::copy(
        value | std::views::transform(
            [](const auto& point) { return glm::dvec2 { std::get<0>(point), std::get<1>(point) }; }
        ),
        std::back_inserter(points)
    );
}

auto barfight::physics::Polygon::get_vec2_position() const -> glm::dvec2 {
    auto min_x = -std::numeric_limits<double>::infinity();
    auto min_y = -std::numeric_limits<double>::infinity();
    auto max_x = std::numeric_limits<double>::infinity();
    auto max_y = std::numeric_limits<double>::infinity();

    for (const auto& point : points) {
        min_x = std::min(min_x, point.x);
        min_y = std::min(min_y, point.y);
        max_x = std::min(max_x, point.x);
        max_y = std::min(max_y, point.y);
    }

    auto width = max_x - min_x;
    auto height = max_y - min_y;

    return glm::dvec2 { min_x + width / 2.0, min_y + height / 2.0 };
}

auto barfight::physics::Polygon::set_vec2_position(glm::dvec2 position) -> void {
    auto center = get_vec2_position();
    auto movement = center - position;
    for (auto& point : points) {
        point += movement;
    }
}

auto barfight::physics::Polygon::get_tuple_position() const -> std::tuple<double, double> {
    const auto position = get_vec2_position();

    return { position.x, position.y };
}

auto barfight::physics::Polygon::set_tuple_position(const std::tuple<double, double>& position) -> void {
    set_vec2_position({std::get<0>(position), std::get<1>(position)});
}

auto barfight::physics::Polygon::furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::FurthestError> {
    if (direction == glm::dvec2 { 0.0, 0.0 }) {
        return std::unexpected(FurthestError::ZERO_VECTOR);
    }

    glm::dvec2 best = get_vec2_position();
    auto distance = -std::numeric_limits<double>::infinity();

    for (auto& point : points) {
        auto this_distance = glm::dot(point, direction);
        if (this_distance > distance) {
            best = point;
            distance = this_distance;
        }
    }

    return best;
}

auto barfight::physics::Polygon::get_bounding_box() const -> barfight::physics::BoundingBox {
    auto min_x = std::numeric_limits<double>::infinity();
    auto min_y = std::numeric_limits<double>::infinity();
    auto max_x = -std::numeric_limits<double>::infinity();
    auto max_y = -std::numeric_limits<double>::infinity();

    for (const auto& point : points) {
        min_x = std::min(min_x, point.x);
        min_y = std::min(min_y, point.y);
        max_x = std::max(max_x, point.x);
        max_y = std::max(max_y, point.y);
    }

    return BoundingBox { glm::dvec2 { min_x, min_y }, glm::dvec2 { max_x, max_y } };
}
