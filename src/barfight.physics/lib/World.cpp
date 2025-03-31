#include <bfphysics/World.hpp>

auto barfight::physics::World::add(const barfight::physics::BodyDescriptor& desc) -> barfight::physics::BodyHandle {
    bodies.emplace_back(Body {
        desc.kind,
        desc.shape
    });

    return BodyHandle { bodies.size() - 1 };
}
