#include <boost/ut.hpp>

import barfight.physics;
import glm;

using namespace boost::ut;

suite<"primitives"> primitives = [] {
    "circle properties set"_test = [] {
        auto c = barfight::physics::Circle { glm::dvec2 { 4.0, 2.0 }, 10.0 };

        expect(4.0 == c.center.x);
        expect(2.0 == c.center.y);
        expect(10.0 == c.radius);
    };

    "rectangle properties set"_test = [] {
        auto r = barfight::physics::Rectangle { glm::dvec2 {1.0, 2.0 }, glm::dvec2 { 3.0, 4.0 } };

        expect(1.0 == r.origin.x);
        expect(2.0 == r.origin.y);
        expect(3.0 == r.size.x);
        expect(4.0 == r.size.y);
    };
};
