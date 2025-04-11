module;

#include <expected>
#include <ranges>
#include <tuple>
#include <glm/vec2.hpp>
#define GLM_ENABLE_EXPERIMENTAL
#include <glm/gtx/rotate_vector.hpp>

export module barfight.physics:OrientedRectangle;
import :BoundingBox;
import :PrimitiveCommon;

namespace barfight::physics {
    export class OrientedRectangle {
        public:
        OrientedRectangle(const glm::dvec2 center, const glm::dvec2 half_size, const double rotation = 0.0)
            : center(center), half_size(half_size), rotation(rotation) {}
        OrientedRectangle(const std::tuple<double, double> center, const std::tuple<double, double> half_size, const double rotation =  0.0)
            : center({ std::get<0>(center), std::get<1>(center) }), half_size({ std::get<0>(half_size), std::get<1>(half_size) }), rotation(rotation) {}

        glm::dvec2 center;
        glm::dvec2 half_size;
        double rotation;

        auto get_center() const -> glm::dvec2 { return center + half_size; }
        auto set_center(glm::dvec2 value) -> void { center = value; }

        auto get_vec2_position() const -> glm::dvec2 { return center; }
        auto set_vec2_position(glm::dvec2 position) -> void { center = position; }

        auto get_tuple_position() const -> std::tuple<double, double> {
            auto position = get_vec2_position();
        
            return { position.x, position.y };
        }

        auto set_tuple_position(const std::tuple<double, double>& position) -> void {
            set_vec2_position({ std::get<0>(position), std::get<1>(position) });
        }

        auto get_tuple_center() const -> std::tuple<double, double> { return { center.x, center.y }; }
        auto set_tuple_center(std::tuple<double, double> value) -> void { center = { std::get<0>(value), std::get<1>(value) }; }
        auto get_tuple_half_size() const -> std::tuple<double, double> { return { half_size.x, half_size.y }; }
        auto set_tuple_half_size(const std::tuple<double, double>& value) -> void {
            half_size = { std::get<0>(value), std::get<1>(value) };
        }

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, FurthestError> {
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

        auto get_bounding_box() const -> BoundingBox {
            double min_x = -std::numeric_limits<double>::infinity();
            double min_y = -std::numeric_limits<double>::infinity();
            double max_x = std::numeric_limits<double>::infinity();
            double max_y = std::numeric_limits<double>::infinity();
        
            for (auto rotation_product : std::views::iota(0, 4)) {
                auto point = glm::rotate(center * half_size, rotation * rotation_product);
                min_x = std::min(min_x, point.x);
                min_y = std::min(min_y, point.y);
                max_x = std::max(max_x, point.x);
                max_y = std::max(max_y, point.y);
            }
            
            return BoundingBox { {min_x, min_y}, {max_x, max_y} };
        }
    };
}
