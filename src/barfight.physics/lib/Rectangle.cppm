module;

#include <expected>

export module barfight.physics:Rectangle;
import glm;
import :BoundingBox;
import :PrimitiveCommon;


namespace barfight::physics {
    export class Rectangle {
        public:
        Rectangle(const glm::dvec2 origin, const glm::dvec2 size) : origin(origin), size(size) {}

        glm::dvec2 origin;
        glm::dvec2 size;

        auto get_center() const -> glm::dvec2 { return origin + (size / 2.0); }
        auto set_center(const glm::dvec2 value) -> void { origin = value - (size / 2.0); }

        auto get_position() const -> glm::dvec2 { return origin + (size / 2.0); }
        auto set_position(const glm::dvec2 position) -> void { origin = position - (size / 2.0); }

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, FurthestError> {
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
