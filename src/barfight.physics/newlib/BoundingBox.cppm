module;
#include <glm/vec2.hpp>

export module barfight.physics:BoundingBox;

namespace barfight::physics {
    export struct BoundingBox {
        glm::dvec2 origin;
        glm::dvec2 size;
    };
}
