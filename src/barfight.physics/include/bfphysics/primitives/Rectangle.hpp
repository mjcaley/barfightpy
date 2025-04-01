#pragma once

#include <expected>
#include <tuple>
#include <bfphysics/primitives/Common.hpp>
#include <glm/vec2.hpp>

namespace barfight::physics::primitives {
    struct Rectangle {
        Rectangle(glm::bvec2 origin, glm::bvec2 size) : origin(origin), size(size) {}
        Rectangle(std::tuple<double, double> origin, std::tuple<double, double> size) :
            origin(glm::dvec2 { std::get<0>(origin), std::get<1>(origin) }),
            size(glm::dvec2 { std::get<0>(size), std::get<1>(size) })
            {}

        glm::dvec2 origin;
        glm::dvec2 size;

        auto get_vec2_position() const -> glm::dvec2;
        auto set_vec2_position(const glm::dvec2& position);
        auto furthest_vec2(const glm::dvec2& direction) const -> glm::dvec2;

        auto get_tuple_position() const -> std::tuple<double, double>;
        auto set_tuple_position(const std::tuple<double, double>& position);
        auto furthest_tuple(const std::tuple<double, double>& direction) -> std::tuple<double, double>;
    };
}
