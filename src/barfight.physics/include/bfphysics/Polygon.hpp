#pragma once

#include <algorithm>
#include <expected>
#include <iterator>
#include <ranges>
#include <tuple>
#include <vector>
#include <bfphysics/PrimitiveCommon.hpp>
#include <glm/vec2.hpp>

namespace barfight::physics {
    struct Polygon {
        Polygon(std::vector<glm::dvec2> points) : points(points) {}
        Polygon(const std::vector<std::tuple<double, double>>& _points) {
            std::ranges::copy(
                _points | std::views::transform(
                    [](const auto& point) { return glm::dvec2 { std::get<0>(point), std::get<1>(point) }; }
                ),
                std::back_inserter(points)
            );
        }

        std::vector<glm::dvec2> points;

        auto get_tuple_points() const -> std::vector<std::tuple<double, double>>;
        auto set_tuple_points(const std::vector<std::tuple<double, double>>& value) -> void;

        auto get_vec2_position() const -> glm::dvec2;
        auto set_vec2_position(glm::dvec2 position) -> void;

        auto get_tuple_position() const -> std::tuple<double, double>;
        auto set_tuple_position(const std::tuple<double, double>& position) -> void;

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::FurthestError>;
        auto get_bounding_box() const -> BoundingBox;
    };
}
