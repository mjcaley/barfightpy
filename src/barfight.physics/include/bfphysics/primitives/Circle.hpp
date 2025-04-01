#pragma once

#include <expected>
#include <tuple>
#include <bfphysics/primitives/Common.hpp>
#include <glm/vec2.hpp>

namespace barfight::physics::primitives {
    struct Circle {
        Circle(glm::dvec2 center, double radius) : center(center), radius(radius) {}
        Circle(std::tuple<double, double> center, double radius) :
            center(glm::dvec2 { std::get<0>(center), std::get<1>(center) }),
            radius(radius)
            {}

        glm::dvec2 center;
        double radius;

        auto get_tuple_center() const -> std::tuple<double, double>;
        auto set_tuple_center(std::tuple<double, double> value) -> void;

        auto get_vec2_position() const -> glm::dvec2;
        auto set_vec2_position(const glm::dvec2& position);
        auto furthest_vec2(const glm::dvec2& direction) const -> glm::dvec2;

        auto get_tuple_position() const -> std::tuple<double, double>;
        auto set_tuple_position(const std::tuple<double, double>& position);
        auto furthest_tuple(const std::tuple<double, double>& direction) -> std::tuple<double, double>;
    };
}
