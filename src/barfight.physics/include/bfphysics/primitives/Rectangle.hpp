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
        auto set_vec2_position(glm::dvec2 position) -> void;

        auto get_tuple_position() const -> std::tuple<double, double>;
        auto set_tuple_position(const std::tuple<double, double>& position) -> void;
        auto get_tuple_origin() const -> std::tuple<double, double>;
        auto set_tuple_origin(std::tuple<double, double> value) -> void;
        auto get_tuple_size() const -> std::tuple<double, double>;
        auto set_tuple_size(const std::tuple<double, double>& value) -> void;
        
        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::primitives::FurthestError>;
    };
}
