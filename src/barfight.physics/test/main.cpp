#include <boost/ut.hpp>
#include <bfphysics/primitives/Circle.hpp>
#include <bfphysics/primitives/Rectangle.hpp>

namespace ut = boost::ut;

auto main() -> int {
    using namespace ut;

    suite primitives = [] {
        "circle_properties"_test = [] {
            auto c = barfight::physics::primitives::Circle { std::make_tuple(4.0, 2.0), 10.0 };
    
            expect(4.0 == c.center.x);
            expect(2.0 == c.center.y);
            expect(10.0 == c.radius);
        };
        
        "circle_properties"_test = [] {
            auto r = barfight::physics::primitives::Rectangle { std::make_tuple(1.0, 2.0), std::make_tuple(3.0, 4.0) };
    
            expect(1.0 == r.origin.x);
            expect(2.0 == r.origin.y);
            expect(3.0 == r.size.x);
            expect(4.0 == r.size.y);
        };
    };
}
