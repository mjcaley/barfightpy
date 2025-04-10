#pragma once

#include <cstddef>

namespace barfight::physics {
    class BodyHandle {
        private:
        std::size_t id;

        public:
        BodyHandle(std::size_t id) : id(id) {}

        auto get_id() const -> std::size_t {
            return id;
        }

        auto operator==(const BodyHandle& other) const -> bool {
            return id == other.id;
        }
    };
}
