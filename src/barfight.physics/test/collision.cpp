#include <boost/ut.hpp>
#include <bfphysics/Collision.hpp>
#include <bfphysics/primitives/Circle.hpp>
#include <glm/vec2.hpp>

namespace ut = boost::ut;

ut::suite collision = [] {
    using namespace barfight::physics::primitives;
    using namespace boost::ut;

    "collision circle-circle colliding"_test = [] {
        auto c1 = Circle { glm::dvec2 { 0.0, 0.0 }, 1.0 };
        auto c2 = Circle { glm::dvec2 { 1.0, 0.0 }, 1.0 };
        auto result = barfight::physics::colliding(c1, c2);

        expect(true == result.has_value()) << "No collision detected";
        expect(1.0_d == result->depth) << "Penetration depth mismatch";
        expect(1.0_d == result->normal.x) << "Normal x mismatch";
        expect(0.0_d == result->normal.y) << "Normal y mismatch";
    };
};
