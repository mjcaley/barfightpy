module;
#include <functional>

export module barfight.physics:CollisionPair;
import :BodyHandle;

namespace barfight::physics {
    export struct CollisionPair {
        BodyHandle handle1;
        BodyHandle handle2;

        auto operator==(const CollisionPair& other) const -> bool {
            return handle1.get_id() == other.handle1.get_id() &&
                   handle2.get_id() == other.handle2.get_id();
        }
    };
}

namespace std {
    export template<>
    struct hash<barfight::physics::CollisionPair> {
        auto operator()(const barfight::physics::CollisionPair& b) const noexcept -> std::size_t {
            return
                std::hash<barfight::physics::BodyHandle>{}(b.handle1) ^
                std::hash<barfight::physics::BodyHandle>{}(b.handle2);
        }
    };
}
