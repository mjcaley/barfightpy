module;

#include <expected>

export module barfight.physics:Circle;
import glm;
import :BoundingBox;
import :PrimitiveCommon;

namespace barfight::physics {
    export class Circle {
        public:
        Circle(const glm::dvec2 center, const double radius) : center(center), radius(radius) {}

        glm::dvec2 center;
        double radius;

        auto get_center() const -> glm::dvec2 { return center; }
        auto set_center(const glm::dvec2 value) -> void { center = value; }

        auto get_position() const -> glm::dvec2 { return center; }
        auto set_position(const glm::dvec2 position) -> void { center = position; }

        auto get_bounding_box() const -> BoundingBox {
            return { glm::dvec2 { center.x - radius, center.y - radius }, glm::dvec2 { center.x - radius, center.y - radius } };
        }

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, FurthestError> {
            if (glm::dvec2 {0.0, 0.0} == direction) {
                return std::unexpected { FurthestError::ZERO_VECTOR };
            }

            return center + radius * glm::normalize(direction);
        }
    };
}
