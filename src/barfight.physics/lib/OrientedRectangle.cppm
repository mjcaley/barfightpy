module;
#include <algorithm>
#include <expected>
#include <limits>
#include <ranges>
#include <tuple>

export module barfight.physics:OrientedRectangle;
import glm;
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

            glm::dvec2 vertices[] = {
                glm::rotate(half_size, rotation) + center,
                glm::rotate( glm::dvec2{-half_size.x,  half_size.y}, rotation) + center,
                glm::rotate(-glm::dvec2{ half_size.x,  half_size.y}, rotation) + center,
                glm::rotate( glm::dvec2{ half_size.x, -half_size.y}, rotation) + center
            };

            return *std::ranges::max_element(vertices, [&direction](const auto& v1, const auto& v2) {
                return glm::dot(v1, direction) < glm::dot(v2, direction);
            });
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
