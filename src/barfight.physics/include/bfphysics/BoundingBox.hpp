#pragma once
#include <glm/vec2.hpp>

namespace barfight::physics {
    struct BoundingBox {
        const glm::dvec2 origin;
        const glm::dvec2 size;
    };
}
