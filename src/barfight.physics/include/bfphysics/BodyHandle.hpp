#pragma once

#include <cstddef>

namespace barfight::physics {
    class BodyHandle {
        private:
        std::size_t id;

        public:
        BodyHandle(std::size_t id) : id(id) {}

        auto get_id() -> std::size_t const {
            return id;
        }
    };
}
