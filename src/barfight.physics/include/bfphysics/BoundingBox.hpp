#pragma once
#include <glm/vec2.hpp>

namespace barfight::physics {
    struct BoundingBox {
        glm::dvec2 origin;
        glm::dvec2 size;
    };
}
