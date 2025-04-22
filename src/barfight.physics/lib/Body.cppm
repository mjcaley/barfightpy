module;
#include <variant>

export module barfight.physics:Body;
import glm;
import :BodyKind;
import :Shape;

namespace barfight::physics {
    export struct Body {
        BodyKind kind;
        Shape shape;
        glm::dvec2 velocity { 0.0, 0.0 };
    };
}
