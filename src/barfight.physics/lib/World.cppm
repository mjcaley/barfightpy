module;
#include <algorithm>
#include <memory>
#include <optional>
#include <ranges>
#include <set>
#include <tuple>
#include <utility>
#include <vector>
#include <glm/vec2.hpp>

export module barfight.physics:World;
import :Body;
import :BodyDescriptor;
import :BodyHandle;
import :Collision;
import :QuadTree;
import :Shape;
import :BroadCollisionPair;
import :NarrowCollisionPair;

namespace barfight::physics {
    export class World {
        private:
        auto filter_active_bodies() const {
            return bodies
                | std::views::enumerate
                | std::views::filter([](auto&& id_body) {
                    auto& [id, body] = id_body;
                    return body.has_value();
                })
                | std::views::transform([&](auto&& id_body) {
                    auto& [id, _] = id_body;
                    return BodyHandle { static_cast<std::size_t>(id) };
                });
        }

        public:
        World(const glm::dvec2 origin, const glm::dvec2 size) : origin(origin), size(size) {}
        World(const std::tuple<double, double>& origin, const std::tuple<double, double>& size)
            : origin(glm::dvec2 { std::get<0>(origin), std::get<1>(origin) }), size(glm::dvec2 { std::get<0>(size), std::get<1>(size) }) {}

        auto add(const BodyDescriptor& desc) -> BodyHandle {
            auto body = Body {
                desc.kind,
                Shape { desc.shape }
            };
            if (body_free_list.empty()) {
                bodies.emplace_back(body);

                auto handle = BodyHandle { bodies.size() - 1 };
                tree.add(handle);

                return handle;
            }
            else {
                auto handle = BodyHandle { body_free_list.back() };
                body_free_list.pop_back();
                bodies[handle.get_id()] = body;
                tree.add(handle);

                return handle;
            }
        }

        auto remove(const BodyHandle handle) -> void {
            if (bodies.size() < handle.get_id() + 1) {
                return;
            }

            bodies[handle.get_id()] = {};
            body_free_list.emplace_back(handle);

            tree.remove(handle);
        }

        auto clear() -> void {
            bodies.clear();
            body_free_list.clear();
            tree.clear();
        }

        auto get_bounding_box() const -> BoundingBox {
            return BoundingBox { origin, size };
        }

        auto resize(glm::dvec2 new_origin, glm::dvec2 new_size) -> void {
            origin = new_origin;
            size = new_size;
            tree = QuadTreeNode { origin, size, bodies };
            tree.clear();
            for (const auto [id, body]: std::views::enumerate(bodies)) {
                tree.add(BodyHandle { static_cast<std::size_t>(id) });
            }
        }

        auto get(const BodyHandle handle) const -> std::optional<Body> {
            if (bodies.size() < handle.get_id() + 1) {
                return {};
            }

            return bodies[handle.get_id()];
        }

        auto query(const BoundingBox& bounding_box) const -> std::set<BodyHandle> {
            return tree.query(bounding_box);
        }

        auto query(const auto& shape) const -> std::set<BodyHandle> {
            return tree.query(shape.get_bounding_box())
                | std::views::filter([&](auto&& handle) {
                    const auto& body = get(handle);
                    return body->shape.colliding(shape).has_value();
                })
                | std::ranges::to<std::set<BodyHandle>>();
        }

        auto broadphase() const -> std::set<BroadCollisionPair> {
            return filter_active_bodies()
                | std::views::transform([&](auto&& handle) {
                    const auto& body = get(handle);
                    auto collisions = query(body->shape.get_bounding_box());

                    return std::make_tuple(handle, collisions);
                })
                | std::views::transform([](auto&& body_collisions) {
                    auto& [handle, collisions] = body_collisions;

                    return collisions
                    | std::views::filter([handle] (auto&& collision) {
                        return handle.get_id() != collision.get_id();
                    })
                    | std::views::transform([&](auto&& collision) {
                        return BroadCollisionPair {handle, collision};
                    })
                    | std::ranges::to<std::set<BroadCollisionPair>>();
                })
                | std::views::join
                | std::ranges::to<std::set<BroadCollisionPair>>();
        }

        auto narrowphase(const std::set<BroadCollisionPair>& broad_collisions) const -> std::set<NarrowCollisionPair> {
            return broad_collisions
            | std::views::transform([&](auto&& pair) {
                auto& [handle1, handle2] = pair;
                auto& body1 = bodies[handle1.get_id()];
                auto& body2 = bodies[handle2.get_id()];

                if (!body1.has_value() || !body2.has_value()) {
                    return NarrowCollisionPair { handle1, handle2, {} };
                }

                auto collision = body1->shape.colliding(body2->shape);

                return NarrowCollisionPair { handle1, handle2, collision };
            })
            | std::views::filter([](auto&& pair) {
                return pair.collision.has_value();
            })
            | std::ranges::to<std::set<NarrowCollisionPair>>();
        }

        private:
        glm::dvec2 origin;
        glm::dvec2 size;
        std::vector<std::optional<Body>> bodies {};
        std::vector<BodyHandle> body_free_list {};
        QuadTreeNode tree { origin, size, bodies };
    };
}
