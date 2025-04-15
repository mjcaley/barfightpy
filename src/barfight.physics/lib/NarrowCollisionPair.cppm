module;
#include <compare>
#include <optional>

export module barfight.physics:NarrowCollisionPair;
import :BodyHandle;
import :Collision;

namespace barfight::physics {
    export struct NarrowCollisionPair {
        BodyHandle handle1;
        BodyHandle handle2;
        std::optional<Collision> collision;

        auto operator<=>(this const NarrowCollisionPair& self, const NarrowCollisionPair& other) -> std::strong_ordering {
            if (self.handle1 < other.handle1) {
                if (self.handle2 < other.handle2) {
                    return std::strong_ordering::less;
                }
                else if (self.handle2 > other.handle2) {
                    return std::strong_ordering::greater;
                }
            }
            else if (self.handle1 > other.handle1) {
                if (self.handle2 < other.handle2) {
                    return std::strong_ordering::less;
                }
                else if (self.handle2 > other.handle2) {
                    return std::strong_ordering::greater;
                }
            }

            return std::strong_ordering::equal;
        }
    };
}
