#pragma once

#include <optional>
#include <vector>
#include <bfphysics/Body.hpp>
#include <bfphysics/BodyDescriptor.hpp>
#include <bfphysics/BodyHandle.hpp>

namespace barfight::physics {
    class World {
        private:
        std::vector<std::optional<Body>> bodies = {};
        std::vector<std::size_t> body_free_list = {};

        public:
        auto add(const BodyDescriptor& bodyDesc) -> BodyHandle;
    };
}
