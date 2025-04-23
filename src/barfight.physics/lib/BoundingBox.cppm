module;
#include <algorithm>

export module barfight.physics:BoundingBox;
import glm;

namespace barfight::physics {
    export struct BoundingBox {
        glm::dvec2 origin;
        glm::dvec2 size;

        static auto encase(const BoundingBox& b1, const BoundingBox& b2) -> BoundingBox {
            return BoundingBox {
                { std::min(b1.origin.x, b2.origin.x), std::min(b1.origin.y, b2.origin.y) },
                { std::max(b1.size.x, b2.size.x), std::max(b1.size.y, b2.size.y) }
            };
        }
    };
}
