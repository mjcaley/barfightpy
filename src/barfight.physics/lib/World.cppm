module;
#include <memory>
#include <optional>
#include <ranges>
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
        public:
        World(const glm::dvec2 origin, const glm::dvec2 size) : origin(origin), size(size) {}
        World(const std::tuple<double, double>& origin, const std::tuple<double, double>& size)
            : origin(glm::dvec2 { std::get<0>(origin), std::get<1>(origin) }), size(glm::dvec2 { std::get<0>(size), std::get<1>(size) }) {}

        auto broadphase() const -> std::vector<std::pair<BodyHandle, BodyHandle>> {
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

        auto remove(BodyHandle handle) -> void {
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

        auto resize(glm::dvec2 new_origin, glm::dvec2 new_size) -> void {
            origin = new_origin;
            size = new_size;
            tree.clear();
            tree = QuadTreeNode { origin, size, bodies };
            for (const auto [id, body]: std::views::enumerate(bodies)) {
                tree.add(BodyHandle { static_cast<std::size_t>(id) });
            }
        }

        private:
        glm::dvec2 origin;
        glm::dvec2 size;
        std::vector<std::optional<Body>> bodies {};
        std::vector<BodyHandle> body_free_list {};
        QuadTreeNode tree { origin, size, bodies };
    };
}
