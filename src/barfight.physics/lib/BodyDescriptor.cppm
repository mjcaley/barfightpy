module;
#include <variant>

export module barfight.physics:BodyDescriptor;
import :Circle;
import :OrientedRectangle;
import :Polygon;
import :Rectangle;
import :BodyKind;

namespace barfight::physics {
    export struct BodyDescriptor {
        BodyDescriptor(const BodyKind kind, const Circle shape)
            : kind(kind), shape(shape) {}
        BodyDescriptor(const BodyKind kind, const OrientedRectangle shape)
            : kind(kind), shape(shape) {}
        BodyDescriptor(const BodyKind kind, const Polygon shape)
            : kind(kind), shape(shape) {}
        BodyDescriptor(const BodyKind kind, const Rectangle shape)
            : kind(kind), shape(shape) {}
        BodyDescriptor(const BodyKind kind, const std::variant<Circle, OrientedRectangle, Polygon, Rectangle> shape)
            : kind(kind), shape(shape) {}

        BodyKind kind;
        std::variant<Circle, OrientedRectangle, Polygon, Rectangle> shape;
    };
}
