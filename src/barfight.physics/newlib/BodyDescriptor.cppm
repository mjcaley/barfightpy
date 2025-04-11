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
        BodyDescriptor(const BodyKind kind, const barfight::physics::Circle shape)
            : kind(kind), shape(shape) {}
        BodyDescriptor(const BodyKind kind, const barfight::physics::OrientedRectangle shape)
            : kind(kind), shape(shape) {}
        BodyDescriptor(const BodyKind kind, const barfight::physics::Polygon shape)
            : kind(kind), shape(shape) {}
        BodyDescriptor(const BodyKind kind, const barfight::physics::Rectangle shape)
            : kind(kind), shape(shape) {}
        BodyDescriptor(const BodyKind kind, const std::variant<barfight::physics::Circle, barfight::physics::OrientedRectangle, barfight::physics::Polygon, barfight::physics::Rectangle> shape)
            : kind(kind), shape(shape) {}

        BodyKind kind;
        std::variant<barfight::physics::Circle, barfight::physics::OrientedRectangle, barfight::physics::Polygon, barfight::physics::Rectangle> shape;
    };
}
