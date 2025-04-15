module;
#include <functional>
#include <optional>

export module barfight.physics:NarrowCollisionPair;
import :BodyHandle;
import :Collision;

namespace barfight::physics {
    export struct NarrowCollisionPair {
        BodyHandle handle1;
        BodyHandle handle2;
        std::optional<Collision> collision;

        auto operator==(const NarrowCollisionPair& other) const -> bool {
            return handle1.get_id() == other.handle1.get_id() &&
                   handle2.get_id() == other.handle2.get_id();
        }
    };
}

namespace std {
    export template<>
    struct hash<barfight::physics::NarrowCollisionPair> {
        auto operator()(const barfight::physics::NarrowCollisionPair& b) const noexcept -> std::size_t {
            return
                std::hash<barfight::physics::BodyHandle>{}(b.handle1) ^
                std::hash<barfight::physics::BodyHandle>{}(b.handle2);
        }
    };
}
