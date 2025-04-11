module;
#include <variant>

export module barfight.physics:Body;
import :BodyKind;
import :Shape;

namespace barfight::physics {
    export struct Body {
        BodyKind kind;
        Shape shape;
    };
}
