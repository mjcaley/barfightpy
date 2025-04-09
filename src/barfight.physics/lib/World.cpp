#include <bfphysics/World.hpp>

auto barfight::physics::World::add(const barfight::physics::BodyDescriptor& desc) -> barfight::physics::BodyHandle {
    auto body = Body {
        desc.kind,
        desc.shape
    };

    if (body_free_list.empty()) {
        bodies.emplace_back(body);

        return BodyHandle { bodies.size() - 1 };
    }
    else {
        auto handle = BodyHandle { body_free_list.back() };
        body_free_list.pop_back();
        bodies[handle.get_id()] = body;

        return handle;
    }
}

auto barfight::physics::World::remove(barfight::physics::BodyHandle handle) -> void {
    if (bodies.size() < handle.get_id() + 1) {
        return;
    }

    bodies[handle.get_id()] = {};
    body_free_list.emplace_back(handle);
}

auto barfight::physics::World::clear() -> void {
    bodies.clear();
    body_free_list.clear();
    tree.clear();
}
