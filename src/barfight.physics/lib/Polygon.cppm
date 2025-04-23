module;

#include <algorithm>
#include <expected>
#include <iterator>
#include <ranges>
#include <vector>

export module barfight.physics:Polygon;
import glm;
import :BoundingBox;
import :PrimitiveCommon;

namespace barfight::physics {
    export class Polygon {
        public:
        Polygon(std::vector<glm::dvec2> points) : points(points) {}

        std::vector<glm::dvec2> points;

        auto get_position() const -> glm::dvec2 {
            auto min_x = std::numeric_limits<double>::infinity();
            auto min_y = std::numeric_limits<double>::infinity();
            auto max_x = -std::numeric_limits<double>::infinity();
            auto max_y = -std::numeric_limits<double>::infinity();

            for (const auto& point : points) {
                min_x = std::min(min_x, point.x);
                min_y = std::min(min_y, point.y);
                max_x = std::max(max_x, point.x);
                max_y = std::max(max_y, point.y);
            }

            auto width = max_x - min_x;
            auto height = max_y - min_y;

            return glm::dvec2 { min_x + width / 2.0, min_y + height / 2.0 };
        }

        auto set_position(const glm::dvec2 position) -> void {
            const auto center = get_position();
            const auto movement = center - position;
            for (auto& point : points) {
                point += movement;
            }
        }

        auto furthest(const glm::dvec2& direction) const -> std::expected<glm::dvec2, FurthestError> {
            if (glm::dvec2 {0.0, 0.0} == direction) {
                return std::unexpected { FurthestError::ZERO_VECTOR };
            }

            return *std::ranges::max_element(points, [&direction](const auto& v1, const auto& v2) {
                return glm::dot(v1, direction) < glm::dot(v2, direction);
            });
        }

        auto get_bounding_box() const -> BoundingBox {
            auto min_x = std::numeric_limits<double>::infinity();
            auto min_y = std::numeric_limits<double>::infinity();
            auto max_x = -std::numeric_limits<double>::infinity();
            auto max_y = -std::numeric_limits<double>::infinity();

            for (const auto& point : points) {
                min_x = std::min(min_x, point.x);
                min_y = std::min(min_y, point.y);
                max_x = std::max(max_x, point.x);
                max_y = std::max(max_y, point.y);
            }

            return BoundingBox { glm::dvec2 { min_x, min_y }, glm::dvec2 { max_x, max_y } };
        }
    };
}
