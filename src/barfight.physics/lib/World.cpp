#include <ranges>
#include <bfphysics/Collision.hpp>
#include <bfphysics/World.hpp>

auto barfight::physics::World::add(const barfight::physics::BodyDescriptor& desc) -> barfight::physics::BodyHandle {
    auto body = Body {
        desc.kind,
        Shape { desc.shape }
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

auto barfight::physics::World::broadphase() const -> std::vector<std::pair<BodyHandle, BodyHandle>> {
    std::vector<std::pair<BodyHandle, BodyHandle>> pairs {};

    for (const auto [id1, body1] : std::views::enumerate(bodies)) {
        if (!body1.has_value()) {
            continue;
        }

        for (const auto [id2, body2] : std::views::enumerate(bodies)) {
            if (!body2.has_value()) {
                continue;
            }

            if (id1 == id2) {
                continue;
            }

            if (overlaps(body1->shape.get_bounding_box(), body2->shape.get_bounding_box())) {
                pairs.emplace_back(
                    BodyHandle { static_cast<std::size_t>(id1) },
                    BodyHandle { static_cast<std::size_t>(id2) }
                );
            }
        }
    }

    return pairs;
}

auto barfight::physics::World::narrowphase(const std::vector<std::pair<BodyHandle, BodyHandle>>& broad_collisions) const -> std::vector<std::tuple<BodyHandle, BodyHandle, collision>> {
    std::vector<std::tuple<BodyHandle, BodyHandle, collision>> collisions {};

    for (auto [handle1, handle2] : broad_collisions) {
        auto& body1 = bodies[handle1.get_id()];
        auto& body2 = bodies[handle2.get_id()];

        if (!body1.has_value() || !body2.has_value()) {
            continue;
        }

        auto collision = body1->shape.colliding(body2->shape);

        if (collision.has_value()) {
            collisions.emplace_back(handle1, handle2, collision.value());
        }
    }

    return collisions;
}
