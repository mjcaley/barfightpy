module;
#include <algorithm>
#include <memory>
#include <optional>
#include <ranges>
#include <set>
#include <tuple>
#include <vector>
#include <glm/vec2.hpp>

export module barfight.physics:World;
import :Body;
import :BodyDescriptor;
import :BodyHandle;
import :Collision;
import :QuadTree;
import :Shape;

namespace barfight::physics {
    export class World {
        private:
        auto filter_active_bodies() const {
            return bodies
                | std::views::enumerate
                | std::views::filter([](const auto id_body) {
                    const auto [id, body] = id_body;
                    return body.has_value();
                })
                | std::views::transform([](const auto id_body) {
                    const auto [id, body] = id_body;
                    return std::make_tuple(BodyHandle { static_cast<std::size_t>(id) }, *body);
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

        auto query(const BoundingBox& bounding_box) -> std::vector<std::tuple<BodyHandle, Body>> {
            return tree.query(bounding_box)
                | std::views::transform([this](const auto& handle) {
                    const auto& body = get(handle);
                    return std::make_tuple(handle, body);
                })
                | std::views::filter([](const auto& handle_body) {
                    const auto [handle, body] = handle_body;
                    return body.has_value();
                })
                | std::views::transform([](const auto& handle_body) {
                    const auto [handle, body] = handle_body;
                    return std::make_tuple(handle, *body);
                })
                | std::ranges::to<std::vector<std::tuple<BodyHandle, Body>>>();
        }

        auto query(const auto& shape) -> std::vector<std::tuple<BodyHandle, Body>> {
            return tree.query(shape.get_bounding_box())
                | std::views::transform([this](const auto& handle) {
                    const auto& body = get(handle);
                    return std::make_tuple(handle, body);
                })
                | std::views::filter([](const auto& handle_body) {
                    const auto [handle, body] = handle_body;
                    return body.has_value();
                })
                | std::views::transform([](const auto& handle_body) {
                    const auto [handle, body] = handle_body;
                    return std::make_tuple(handle, *body);
                })
                | std::views::filter([&](const auto& handle_body) {
                    const auto [handle, body] = handle_body;
                    return body.shape.colliding(shape).has_value();
                })
                | std::ranges::to<std::vector<std::tuple<BodyHandle, Body>>>();
        }

        auto broadphase() const -> std::vector<std::pair<BodyHandle, BodyHandle>> {
            std::vector<std::pair<BodyHandle, BodyHandle>> pairs {};

            for (const auto [handle1, body1] : filter_active_bodies()) {
                auto body_bounding_box = body1.shape.get_bounding_box();
                auto found = tree.query(body_bounding_box);
            }

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

        auto narrowphase(const std::vector<std::pair<BodyHandle, BodyHandle>>& broad_collisions) const -> std::vector<std::tuple<BodyHandle, BodyHandle, Collision>> {
            std::vector<std::tuple<BodyHandle, BodyHandle, Collision>> collisions {};

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

        private:
        glm::dvec2 origin;
        glm::dvec2 size;
        std::vector<std::optional<Body>> bodies {};
        std::vector<BodyHandle> body_free_list {};
        QuadTreeNode tree { origin, size, bodies };
    };
}
