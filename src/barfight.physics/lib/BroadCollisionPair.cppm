module;
#include <set>

export module barfight.physics:BroadCollisionPair;
import :BodyHandle;
import :Body;

namespace barfight::physics {
    export struct BroadCollisionPair {
        BodyHandle handle1;
        BodyHandle handle2;

        auto operator<=>(this const BroadCollisionPair& self, const BroadCollisionPair& other) -> std::strong_ordering {
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
