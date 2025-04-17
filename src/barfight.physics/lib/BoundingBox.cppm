export module barfight.physics:BoundingBox;
import glm;

namespace barfight::physics {
    export struct BoundingBox {
        glm::dvec2 origin;
        glm::dvec2 size;
    };
}
