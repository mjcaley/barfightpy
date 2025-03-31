#pragma once
#include <variant>
#include <bfphysics/BodyKind.hpp>
#include <bfphysics/Shape.hpp>

namespace barfight::physics {
    struct Body {
        BodyKind kind;
        barfight::physics::Shape shape;
    };
}
