#pragma once
#include <bfphysics/BodyKind.hpp>
#include <bfphysics/Shape.hpp>

namespace barfight::physics {
    struct BodyDescriptor {
        BodyKind kind;
        Shape shape;
    };
}
