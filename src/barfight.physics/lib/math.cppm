module;
#include <numbers>

export module barfight.math;

namespace barfight::math {
    export constexpr auto to_radians(auto degrees) -> auto {
        return degrees * std::numbers::pi_v<decltype(degrees)> / 180.0;
    }

    export constexpr auto to_degress(auto radians) -> auto {
        return radians * 180.0 / std::numbers::pi_v<decltype(radians)>;
    }
}
