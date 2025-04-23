module;
#include <algorithm>
#include <functional>
#include <memory>
#include <optional>
#include <ranges>
#include <tuple>
#include <unordered_map>
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
import :ResolvedCollisionPair;
import :Arbiter;

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

        auto get(const BodyHandle handle) -> std::optional<Body>& {
            if (bodies.size() < handle.get_id() + 1) {
                return bodies[0];
            }

            auto& opt_body = bodies[handle.get_id()];
            return opt_body;
        }

        auto query(const auto& shape) -> std::unordered_set<BodyHandle>
            requires (!std::same_as<std::remove_cvref_t<decltype(shape)>, BoundingBox>) {
            return tree.query(shape.get_bounding_box())
                | std::views::filter([&](auto&& handle) {
                    auto& body = get(handle);
                    if (!body) {
                        return false;
                    }

                    return body->shape.colliding(shape).has_value();
                })
                | std::ranges::to<std::unordered_set<BodyHandle>>();
        }

        auto query(const BoundingBox& bounding_box) const -> std::unordered_set<BodyHandle> {
            return tree.query(bounding_box);
        }

        auto time_of_impact(const BodyHandle handle, const double dt) -> std::optional<TimeOfImpact> {
            auto& body = get(handle);
            if (!body) {
                return {};
            }

            // get bounding box for body movement
            auto box_at_dest = body->shape.get_bounding_box();
            box_at_dest.origin = box_at_dest.origin * body->velocity * dt;
            const auto movement_box = BoundingBox::encase(body->shape.get_bounding_box(), box_at_dest);

            // get all colliding bodies of bounding box
            const auto bodies = query(movement_box);

            // filter bodies that aren't Static
            // bodies
            // | std::views::filter([&](auto&& b) {
            //     return &body != &b;
            // })
            // | std::views::filter([&](auto&& b) {
            //     return barfight::physics::time_of_impact(b.shape, box_at_dest); // Need a rect?
            // })

            // get shortest time to impact of remaining bodies
        }

        auto broadphase() -> std::unordered_set<CollisionPair> {
            return filter_active_bodies()
                | std::views::transform([&](auto&& handle) {
                    auto& body = get(handle);
                    auto collisions = query(body->shape.get_bounding_box());

                    return std::make_tuple(handle, collisions);
                })
                | std::views::transform([](auto&& body_collisions) {
                    auto [handle, collisions] = body_collisions;

                    return collisions
                    | std::views::filter([handle] (auto&& collision) {
                        return handle.get_id() != collision.get_id();
                    })
                    | std::views::transform([&](auto&& collision) {
                        return CollisionPair {handle, collision};
                    })
                    | std::ranges::to<std::unordered_set<CollisionPair>>();
                })
                | std::views::join
                | std::ranges::to<std::unordered_set<CollisionPair>>();
        }

        auto narrowphase(const std::unordered_set<CollisionPair>& broad_collisions) -> std::unordered_map<CollisionPair, Collision> {
            return
            broad_collisions
            | std::views::filter([&](auto&& pair) {
                auto [handle1, handle2] = pair;

                return get(handle1) && get(handle2);
            })
            | std::views::transform([&](auto&& pair) {
                auto [handle1, handle2] = pair;
                const auto& body1 = get(handle1);
                const auto& body2 = get(handle2);
                auto collision = std::optional<Collision> {};

                if (!body1 || !body2) {
                    return std::make_tuple(handle1, handle2, collision);
                }

                collision = body1->shape.colliding(body2->shape);

                return std::make_tuple(handle1, handle2, collision);
            })
            | std::views::filter([](auto&& pair) {
                return std::get<2>(pair).has_value();
            })
            | std::views::transform([](auto&& pair) {
                auto [handle1, handle2, collision] = pair;

                return std::make_pair(
                    CollisionPair { handle1, handle2 },
                    *collision
                );
            })
            | std::ranges::to<std::unordered_map<CollisionPair, Collision>>();
        }

        auto set_on_collision_callback(std::function<void(BodyHandle, Arbiter)> callback) -> void {
            on_collision_callback = callback;
        }

        auto clear_on_collision_callback() -> void {
            on_collision_callback = [](BodyHandle, Arbiter) { };
        }

        auto set_on_sensor_callback(std::function<void(BodyHandle, Arbiter)> callback) -> void {
            on_sensor_callback = callback;
        }

        auto clear_on_sensor_callback() -> void {
            on_sensor_callback = [](BodyHandle, Arbiter) { };
        }

        auto set_on_position_change_callback(std::function<void(BodyHandle)> callback) -> void {
            on_position_change_callback = callback;
        }

        auto clear_on_position_change_callback() -> void {
            on_position_change_callback = [](BodyHandle) { };
        }

        auto step(double dt) -> void {
            collisions(dt);
        }

        private:
        glm::dvec2 origin;
        glm::dvec2 size;
        std::vector<std::optional<Body>> bodies { {} };
        std::vector<BodyHandle> body_free_list {};
        QuadTreeNode tree { origin, size, bodies };
        std::function<void(BodyHandle, Arbiter)> on_collision_callback = [](BodyHandle, Arbiter) { };
        std::function<void(BodyHandle, Arbiter)> on_sensor_callback = [](BodyHandle, Arbiter) { };
        std::function<void(BodyHandle)> on_position_change_callback = [](BodyHandle) { };

        auto collisions(double dt) -> void {
            auto broad_collisions = broadphase();
            auto narrow_collisions = narrowphase(broad_collisions);
            // auto resolved_collisions = resolve(narrow_collisions);
            resolve(narrow_collisions);
            // set active collisions
        }

        auto resolve(const std::unordered_map<CollisionPair, Collision>& narrow_collisions) -> void {
            auto resolved = std::unordered_set<CollisionPair> {};
            auto still_colliding = std::unordered_set<CollisionPair> {};

            for (const auto& [pair, _] : narrow_collisions) {
                auto& body1 = get(pair.handle1);
                auto& body2 = get(pair.handle2);

                if (!body1 || !body2) {
                    continue;
                }

                if (body1->kind == BodyKind::DYNAMIC && body2->kind == BodyKind::STATIC) {
                    auto collision = body1->shape.colliding(body2->shape);
                    if (!collision) {
                        resolved.insert(pair);
                        continue;
                    }

                    body1->shape.set_position(
                        body1->shape.get_position() -
                        collision->normal * collision->depth);
                    resolved.insert(pair);

                    // create arbiter
                    on_position_change_callback(pair.handle1);
                    on_collision_callback(pair.handle1, Arbiter { pair.handle1, pair.handle2, true });
                }
                else if (body1->kind == BodyKind::DYNAMIC && body2->kind == BodyKind::SENSOR) {
                    auto collision = body1->shape.colliding(body2->shape);
                    if (!collision) {
                        resolved.insert(pair);
                        continue;
                    }

                    // create arbiter
                    on_sensor_callback(pair.handle1, Arbiter { pair.handle1, pair.handle2, true });
                }
            }
        }
    };
}
