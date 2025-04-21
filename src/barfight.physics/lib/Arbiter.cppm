export module barfight.physics:Arbiter;
import :BodyHandle;

namespace barfight::physics {
    export struct Arbiter {
        BodyHandle handle1;
        BodyHandle handle2;
        bool is_first_collision;
    };
}
