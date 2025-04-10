#pragma once
#include <expected>
#include <tuple>
#include <glm/glm.hpp>
#include <bfphysics/BoundingBox.hpp>
#include <bfphysics/PrimitiveCommon.hpp>

namespace barfight::physics {
    class OrientedRectangle {
        public:
        OrientedRectangle(const glm::dvec2 center, const glm::dvec2 half_size, const double rotation = 0.0)
            : center(center), half_size(half_size), rotation(rotation) {}
        OrientedRectangle(const std::tuple<double, double> center, const std::tuple<double, double> half_size, const double rotation =  0.0)
            : center({ std::get<0>(center), std::get<1>(center) }), half_size({ std::get<0>(half_size), std::get<1>(half_size) }), rotation(rotation) {}

        glm::dvec2 center;
        glm::dvec2 half_size;
        double rotation;

        auto get_center() const -> glm::dvec2;
        auto set_center(glm::dvec2 value) -> void;

        auto get_vec2_position() const -> glm::dvec2;
        auto set_vec2_position(glm::dvec2 position) -> void;

        auto get_tuple_position() const -> std::tuple<double, double>;
        auto set_tuple_position(const std::tuple<double, double>& position) -> void;
        auto get_tuple_center() const -> std::tuple<double, double>;
        auto set_tuple_center(std::tuple<double, double> value) -> void;
        auto get_tuple_half_size() const -> std::tuple<double, double>;
        auto set_tuple_half_size(const std::tuple<double, double>& value) -> void;

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::FurthestError>;
        auto get_bounding_box() const -> BoundingBox;
    };
}
