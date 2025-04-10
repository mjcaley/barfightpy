#pragma once

#include <variant>
#include <bfphysics/Circle.hpp>
#include <bfphysics/OrientedRectangle.hpp>
#include <bfphysics/Polygon.hpp>
#include <bfphysics/Rectangle.hpp>
#include <bfphysics/BodyKind.hpp>

namespace barfight::physics {
    struct BodyDescriptor {
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
