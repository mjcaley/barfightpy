#pragma once

#include <optional>
#include <vector>
#include <bfphysics/Body.hpp>
#include <bfphysics/BodyDescriptor.hpp>
#include <bfphysics/BodyHandle.hpp>
#include <bfphysics/QuadTree.hpp>

namespace barfight::physics {
    class World {
        public:
        World(const glm::dvec2 origin, const glm::dvec2 size) :
            origin(origin), size(size) {}
        World(const std::tuple<double, double>& origin, const std::tuple<double, double>& size) :
            origin(glm::dvec2 { std::get<0>(origin), std::get<1>(origin) }),
            size(glm::dvec2 { std::get<0>(size), std::get<1>(size) }) {}

        auto add(const BodyDescriptor& bodyDesc) -> BodyHandle;
        auto remove(BodyHandle handle) -> void;
        auto clear() -> void;

        private:
        glm::dvec2 origin;
        glm::dvec2 size;
        std::vector<std::optional<Body>> bodies {};
        std::vector<BodyHandle> body_free_list {};
        barfight::physics::QuadTreeNode tree { origin, size };
    };
}
