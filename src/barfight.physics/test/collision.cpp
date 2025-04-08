#include <numbers>
#include <boost/ut.hpp>
#include <bfphysics/Collision.hpp>
#include <bfphysics/Circle.hpp>
#include <bfphysics/Rectangle.hpp>
#include <glm/vec2.hpp>
#include <glm/geometric.hpp>
#include <glm/gtx/rotate_vector.hpp>

namespace ut = boost::ut;

ut::suite collision = [] {
    using namespace barfight::physics;
    using namespace boost::ut;

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
    };
};
