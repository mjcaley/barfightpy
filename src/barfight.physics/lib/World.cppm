module;
#include <algorithm>
#include <functional>
#include <map>
#include <memory>
#include <optional>
#include <ranges>
#include <tuple>
#include <unordered_set>
#include <utility>
#include <vector>

export module barfight.physics:World;
import glm;
import :Body;
import :BodyDescriptor;
import :BodyHandle;
import :Collision;
import :QuadTree;
import :Shape;
import :CollisionPair;
import :BroadCollisionPair;
import :NarrowCollisionPair;
import :ResolvedCollisionPair;

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

        auto get(const BodyHandle handle) const -> Body* {
            if (bodies.size() < handle.get_id() + 1) {
                return nullptr;
            }

            auto& opt_body = bodies[handle.get_id()];
            return opt_body ? &(*opt_body) : nullptr;
        }

        auto query(const BoundingBox& bounding_box) const -> std::unordered_set<BodyHandle> {
            return tree.query(bounding_box);
        }

        auto query(const auto& shape) const -> std::unordered_set<BodyHandle> {
            return tree.query(shape.get_bounding_box())
                | std::views::filter([&](auto&& handle) {
                    auto* body = get(handle);
                    if (!body) {
                        return false;
                    }

                    return body->shape.colliding(shape).has_value();
                })
                | std::ranges::to<std::unordered_set<BodyHandle>>();
        }

        auto broadphase() const -> std::unordered_set<BroadCollisionPair> {
            return filter_active_bodies()
                | std::views::transform([&](auto&& handle) {
                    auto* body = get(handle);
                    if (!body) {
                        return false;
                    }

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
                    | std::ranges::to<std::unordered_set<BroadCollisionPair>>();
                })
                | std::views::join
                | std::ranges::to<std::unordered_set<BroadCollisionPair>>();
        }

        auto narrowphase(const std::unordered_set<BroadCollisionPair>& broad_collisions) const -> std::map<CollisionPair, Collision> {
            return broad_collisions
            | std::views::filter([&](auto&& pair) {
                auto [handle1, handle2] = pair;

                return get(handle1) && get(handle2);
            })
            | std::views::transform([&](auto&& pair) {
                auto& [handle1, handle2] = pair;
                auto* body1 = get(handle1);
                auto* body2 = get(handle1);
                if (!body1 || !body2) {
                    return std::make_tuple(std::nullopt, std::nullopt, std::nullopt);
                }

                auto collision = body1->shape.colliding(body2->shape);

                return std::make_tuple(handle1, handle2, collision);
                // return NarrowCollisionPair { handle1, handle2, collision };
            })
            | std::views::filter([](auto&& pair) {
                return std::get<0>(pair).has_value() && std::get<1>(pair).has_value() && std::get<2>(pair).has_value();
            })
            | std::views::transform([](auto&& pair) {
                auto [handle1, handle2, collision] = pair;

                return std::make_pair(
                    CollisionPair { handle1, handle2 },
                    *collision
                );
            })
            | std::ranges::to<std::map<CollisionPair, Collision>>();
        }

        auto step(double dt) -> void {
            get_collisions(dt);
        }

        private:
        glm::dvec2 origin;
        glm::dvec2 size;
        std::vector<std::optional<Body>> bodies {};
        std::vector<BodyHandle> body_free_list {};
        QuadTreeNode tree { origin, size, bodies };

        auto get_collisions(double dt) -> void {
            auto broad_collisions = broadphase();
            auto narrow_collisions = narrowphase(broad_collisions);
            // auto resolved_collisions = resolve(narrow_collisions);
            resolve(narrow_collisions);
            // set active collisions
        }

        auto resolve(const std::unordered_set<NarrowCollisionPair>& narrow_collisions) -> void {
            auto resolved = std::unordered_set<ResolvedCollisionPair> {};
            auto still_colliding = std::unordered_set<NarrowCollisionPair> {}; // TODO: another type?

            for (const auto& nc : narrow_collisions) {
                const auto& body1 = get(nc.handle1);
                const auto& body2 = get(nc.handle2);

                if (!body1 || !body2) {
                    continue;
                }

                if (body1->kind == BodyKind::DYNAMIC && body2->kind == BodyKind::STATIC) {

                }
                else if (body1->kind == BodyKind::DYNAMIC && body2->kind == BodyKind::SENSOR) {

                }
            }
        }
    };
}
