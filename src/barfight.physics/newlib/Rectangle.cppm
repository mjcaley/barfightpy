module;

#include <expected>
#include <tuple>
#include <glm/vec2.hpp>

export module barfight.physics:Rectangle;
import :BoundingBox;
import :PrimitiveCommon;


namespace barfight::physics {
    export class Rectangle {
        public:
        Rectangle(glm::dvec2 origin, glm::dvec2 size) : origin(origin), size(size) {}
        Rectangle(std::tuple<double, double> origin, std::tuple<double, double> size) :
            origin(glm::dvec2 { std::get<0>(origin), std::get<1>(origin) }),
            size(glm::dvec2 { std::get<0>(size), std::get<1>(size) })
            {}

        glm::dvec2 origin;
        glm::dvec2 size;

        auto get_center() const -> glm::dvec2 { return origin + (size / 2.0); }
        auto set_center(glm::dvec2 value) -> void { origin = value - (size / 2.0); }

        auto get_vec2_position() const -> glm::dvec2 { return origin + (size / 2.0); }
        auto set_vec2_position(glm::dvec2 position) -> void { origin = position - (size / 2.0); }

        auto get_tuple_position() const -> std::tuple<double, double> {
            auto position = get_vec2_position();
        
            return { position.x, position.y };
        }

        auto set_tuple_position(const std::tuple<double, double>& position) -> void {
            set_vec2_position({ std::get<0>(position), std::get<1>(position) });
        }

        auto get_tuple_origin() const -> std::tuple<double, double> { return { origin.x, origin.y }; }
        auto set_tuple_origin(std::tuple<double, double> value) -> void { origin = { std::get<0>(value), std::get<1>(value) }; }
        auto get_tuple_size() const -> std::tuple<double, double> { return { size.x, size.y }; }
        auto set_tuple_size(const std::tuple<double, double>& value) -> void { size = { std::get<0>(value), std::get<1>(value) }; }

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, barfight::physics::FurthestError> {
            using barfight::physics::FurthestError;
        
            if (glm::dvec2 {0.0, 0.0} == direction) {
                return std::unexpected { FurthestError::ZERO_VECTOR };
            }
        
            if (direction.x <= 0 && direction.y <= 0) {
                return origin;
            }
            else if (direction.x <= 0 && direction.y >= 0) {
                return glm::dvec2 { origin.x, origin.y + size.y };
            }
            else if (direction.x >= 0 && direction.y >= 0) {
                return origin + size;
            }
            else {
                return glm::dvec2 { origin.x + size.x, origin.y };
            }
        }

        auto get_bounding_box() const -> BoundingBox {
            return BoundingBox {
                origin,
                size
            };
        }
    };
}
