module;
#include <compare>
#include <cstddef>
#include <functional>

export module barfight.physics:BodyHandle;

namespace barfight::physics {
    export class BodyHandle {
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

        auto operator<=>(const BodyHandle& other) const -> std::strong_ordering {
            if (id < other.id) { return std::strong_ordering::less; }
            else if (id == other.id) { return std::strong_ordering::equal; }
            else { return std::strong_ordering::greater; }
        }
    };
}

namespace std {
    export template<>
    struct hash<barfight::physics::BodyHandle> {
        auto operator()(const barfight::physics::BodyHandle& b) const noexcept -> std::size_t {
            return std::hash<std::size_t>{}(b.get_id());
        }
    };
}
