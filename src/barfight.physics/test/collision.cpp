#include <numbers>
#include <boost/ut.hpp>

import barfight.math;
import barfight.physics;
import glm;

using namespace boost::ut;

suite<"collision"> collision = [] {
    using namespace barfight::math;
    using namespace barfight::physics;

    "furthest point rectangle"_test = [] {
        const auto r1 = Rectangle { glm::dvec2 { 0.0, 0.0 }, glm::dvec2 { 1.0, 1.0 }};

        expect(r1.furthest(glm::normalize( glm::dvec2 { 1.0, 1.0 })) == glm::dvec2 {1.0, 1.0}) << "top right point\n";
        expect(r1.furthest(glm::normalize( glm::dvec2 { 1.0, -1.0 })) == glm::dvec2 {1.0, 0.0}) << "bottom right point\n";
        expect(r1.furthest(glm::normalize( glm::dvec2 { -1.0, -1.0 })) == glm::dvec2 {0.0, 0.0}) << "bottom left point\n";
        expect(r1.furthest(glm::normalize( glm::dvec2 { -1.0, 1.0 })) == glm::dvec2 {0.0, 1.0}) << "top left point\n";
    };

    "furthest point circle"_test = [] {
        const auto c1 = Circle { glm::dvec2 { 0.0, 0.0 }, 1.0 };

        auto top_right_result = c1.furthest(glm::normalize(glm::dvec2 { 1.0, 1.0 }));
        expect(top_right_result.has_value()) << "top right point error\n";
        expect(0.7071_d == top_right_result.value().x) << "top right point x mismatch\n";
        expect(0.7071_d == top_right_result.value().y) << "top right point y mismatch\n";

        auto bottom_right_result = c1.furthest(glm::normalize(glm::dvec2 { 1.0, -1.0 }));
        expect(bottom_right_result.has_value()) << "bottom right point error\n";
        expect(0.7071_d == bottom_right_result.value().x) << "bottom right point x mismatch\n";
        expect(-0.7071_d == bottom_right_result.value().y) << "bottom right point y mismatch\n";

        auto top_left_result = c1.furthest(glm::normalize(glm::dvec2 { -1.0, -1.0 }));
        expect(top_left_result.has_value()) << "top left point error\n";
        expect(-0.7071_d == top_left_result.value().x) << "top right left x mismatch\n";
        expect(-0.7071_d == top_left_result.value().y) << "top right left y mismatch\n";

        auto bottom_left_result = c1.furthest(glm::normalize(glm::dvec2 { -1.0, 1.0 }));
        expect(bottom_left_result.has_value()) << "bottom left point error\n";
        expect(-0.7071_d == bottom_left_result.value().x) << "top bottom left point x mismatch\n";
        expect(0.7071_d == bottom_left_result.value().y) << "top bottom left point y mismatch\n";
    };

    "collision circle-circle colliding"_test = [] {
        const auto c1 = Circle { glm::dvec2 { 0.0, 0.0 }, 1.0 };
        const auto c2 = Circle { glm::dvec2 { 1.0, 0.0 }, 1.0 };
        const auto result = colliding(c1, c2);

        expect(true == result.has_value()) << "No collision detected\n";
        expect(1.0_d == result->depth) << "Penetration depth mismatch\n";
        expect(1.0_d == result->normal.x) << "Normal x mismatch\n";
        expect(0.0_d == result->normal.y) << "Normal y mismatch\n";
    };

    "collision rectangle-rectangle colliding"_test = [] {
        const auto r1 = Rectangle { glm::dvec2 { 0.0, 0.0 }, glm::dvec2 { 1.0, 1.0 }};
        const auto r2 = Rectangle { glm::dvec2 { 0.5, 0.0 }, glm::dvec2 { 1.0, 1.0 }};
        const auto result = colliding(r1, r2);

        expect(true == result.has_value()) << "No collision detected\n";
        expect(0.5_d == result->depth) << "depth incorrect\n";
        expect(1.0_d == result->normal.x) << "normal x mismatch\n";
        expect(0.0_d == result->normal.y) << "normal y mismatch\n";
    };

    "bounding box overlaps"_test = [] {
        using barfight::physics::BoundingBox;
        using barfight::physics::overlaps;

        const auto b1 = BoundingBox { glm::dvec2 { 0.0, 0.0 }, glm::dvec2 { 1.0, 1.0 } };
        const auto b2 = BoundingBox { glm::dvec2 { 0.5, 0.0 }, glm::dvec2 { 1.0, 1.0 } };
        const auto b3 = BoundingBox { glm::dvec2 { 2.0, 0.0 }, glm::dvec2 { 1.0, 1.0 } };

        expect(overlaps(b1, b2)) << "b1 and b2 should overlap but don't\n";
        expect(!overlaps(b1, b3)) << "b1 and b3 don't overlap but do\n";
    };

    "shape collision"_test = []<typename T>(T arg) {
        auto [shape1, shape2] = arg;

        auto result = colliding(shape1, shape2);

        expect(result.has_value()) << "No collision detected\n";
    } | std::tuple {
        std::tuple {
            Rectangle { glm::dvec2 { 0.0, 0.0 }, glm::dvec2 { 1.0, 1.0 }},
            Rectangle { glm::dvec2 { 0.5, 0.0 }, glm::dvec2 { 1.0, 1.0 }}
        },
        std::tuple {
            Circle { glm::dvec2 { 0.0, 0.0 }, 1.0},
            Circle { glm::dvec2 { 0.5, 0.0 }, 1.0}
        },
        std::tuple {
            OrientedRectangle { glm::dvec2 { 0.0, 0.0 }, glm::dvec2 { 5.0, 5.0 }, to_radians(45.0)},
            OrientedRectangle { glm::dvec2 { 0.5, 0.0 }, glm::dvec2 { 5.0, 5.0 }, to_radians(45.0)}
        },
        std::tuple {
            Polygon { {glm::dvec2{4.0, 5.0}, glm::dvec2{4.0, 11.0}, glm::dvec2{9.0, 9.0}} },
            Polygon { {glm::dvec2{7.0, 3.0}, glm::dvec2{5.0, 7.0}, glm::dvec2{12.0, 7.0}, glm::dvec2{10.0, 2.0}} }
        }
    };

    "time of impact"_test = [] {
        const auto r1 = Rectangle { glm::dvec2 {0.0, -5.0}, glm::dvec2 {10.0, 10} };
        const auto r2 = Rectangle { glm::dvec2 {10.5, -5.0}, glm::dvec2 {20.0, 20} };
        const auto velocity = glm::dvec2 { 1.0, 0.0 };
        const auto dt = 1.0;

        const auto result = time_of_impact(r1, r2, velocity, dt);

        expect(fatal(result.has_value())) << "No time of impact detected\n";
        expect(0.5_d == result->time) << "Time of impact mismatch\n";
    };

    "time of impact Shape-Shape"_test = [] {
        const auto s1 = Shape { Rectangle { glm::dvec2 {0.0, -5.0}, glm::dvec2 {10.0, 10} } };
        const auto s2 = Shape { Rectangle { glm::dvec2 {10.5, -5.0}, glm::dvec2 {20.0, 20} } };
        const auto velocity = glm::dvec2 { 1.0, 0.0 };
        const auto dt = 1.0;

        const auto result = s1.time_of_impact(s2, velocity, dt);

        expect(fatal(result.has_value())) << "No time of impact detected\n";
        expect(0.5_d == result->time) << "Time of impact mismatch\n";
    };

    "time of impact Shape-Primitive"_test = [] {
        const auto s1 = Shape { Rectangle { glm::dvec2 {0.0, -5.0}, glm::dvec2 {10.0, 10} } };
        const auto r2 = Rectangle { glm::dvec2 {10.5, -5.0}, glm::dvec2 {20.0, 20} };
        const auto velocity = glm::dvec2 { 1.0, 0.0 };
        const auto dt = 1.0;

        const auto result = s1.time_of_impact(r2, velocity, dt);

        expect(fatal(result.has_value())) << "No time of impact detected\n";
        expect(0.5_d == result->time) << "Time of impact mismatch\n";
    };
};
