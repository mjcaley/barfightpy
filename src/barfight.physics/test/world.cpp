#include <unordered_set>
#include <variant>
#include <boost/ut.hpp>
#include <glm/vec2.hpp>

import barfight.physics;

using namespace boost::ut;

suite<"world"> world = [] {
    using barfight::physics::World;
    using barfight::physics::BoundingBox;
    using barfight::physics::BodyDescriptor;
    using barfight::physics::BodyHandle;
    using barfight::physics::BodyKind;
    using barfight::physics::Shape;
    using barfight::physics::Circle;
    using barfight::physics::BroadCollisionPair;
    using barfight::physics::NarrowCollisionPair;

    "world properties set with defaults"_test = [] {
        auto world = World { glm::dvec2 {0.0, 0.0}, glm::dvec2 {10.0, 10.0} };
        expect(0.0_d == world.get_bounding_box().origin.x) << "origin.x is not 0.0";
        expect(0.0_d == world.get_bounding_box().origin.y) << "origin.y is not 0.0";
        expect(10.0_d == world.get_bounding_box().size.x) << "size.x is not 10.0";
        expect(10.0_d == world.get_bounding_box().size.y) << "size.y is not 10.0";
    };

    "world adds and gets body"_test = [] {
        auto world = World { glm::dvec2 {0.0, 0.0}, glm::dvec2 {10.0, 10.0} };
        auto desc = BodyDescriptor { BodyKind::DYNAMIC, Circle { glm::dvec2 {5.0, 5.0}, 1.0 } };
        auto handle = world.add(desc);
        auto body = world.get(handle);

        expect(fatal(body.has_value())) << "Body doesn't exist in world";
        expect(fatal(holds_alternative<Circle>(body->shape.get_shape()))) << "Body isn't a circle";
        expect(BodyKind::DYNAMIC == body->kind) << "Not a dynamic body";
        expect(1.0_d == std::get<Circle>(body->shape.get_shape()).radius) << "Circle radius isn't correct";
        expect(5.0_d == std::get<Circle>(body->shape.get_shape()).center.x) << "Circle center.x isn't correct";
        expect(5.0_d == std::get<Circle>(body->shape.get_shape()).center.y) << "Circle center.y isn't correct";
    };

    "world removes body"_test = [] {
        auto world = World { glm::dvec2 {0.0, 0.0}, glm::dvec2 {10.0, 10.0} };
        auto desc = BodyDescriptor { BodyKind::DYNAMIC, Circle { glm::dvec2 {5.0, 5.0}, 1.0 } };
        auto handle = world.add(desc);
        world.remove(handle);
        auto body = world.get(handle);

        expect(!body.has_value()) << "Body still exists in world after removal";
    };

    "world query primitive returns bodies"_test = [] {
        auto world = World { glm::dvec2 {0.0, 0.0}, glm::dvec2 {10.0, 10.0} };
        auto desc = BodyDescriptor { BodyKind::DYNAMIC, Circle { glm::dvec2 {5.0, 5.0}, 1.0 } };
        auto handle = world.add(desc);

        auto result = world.query(Circle { glm::dvec2 {5.0, 5.0}, 1.0 });

        expect(fatal(result.size() == 1)) << "Query returned no bodies";
        for (const auto& h : result) {
            expect(handle == h) << "Handles are not the same";
        }
    };

    "world query bounding box returns bodies"_test = [] {
        auto world = World { glm::dvec2 {0.0, 0.0}, glm::dvec2 {10.0, 10.0} };
        auto desc = BodyDescriptor { BodyKind::DYNAMIC, Circle { glm::dvec2 {5.0, 5.0}, 1.0 } };
        auto handle = world.add(desc);

        auto result = world.query(BoundingBox { glm::dvec2 {4.0, 4.0}, glm::dvec2 {6.0, 6.0} });

        expect(fatal(result.size() == 1)) << "Query returned no bodies";
        for (const auto& h : result) {
            expect(handle == h.get_id()) << "Handles are not the same";
        }
    };

    "world returns broadphase collisions"_test = [] {
        auto world = World { glm::dvec2 {0.0, 0.0}, glm::dvec2 {10.0, 10.0} };
        auto handle1 = world.add({
            BodyKind::DYNAMIC,
            Circle { glm::dvec2 {5.0, 5.0}, 1.0 }
        });
        auto handle2 = world.add({
            BodyKind::DYNAMIC,
            Circle { glm::dvec2 {5.0, 5.0}, 1.0 }
        });

        auto results = world.broadphase();

        expect(2 == results.size()) << "Broadphase didn't return 2 collisions";
        expect(results.contains(BroadCollisionPair { handle1, handle2 })) << "Broadphase doesn't contain collision pair 0-1";
        expect(results.contains(BroadCollisionPair { handle2, handle1 })) << "Broadphase doesn't contain collision pair 1-0";
    };

    "world returns narrowphase collisions"_test = [] {
        auto world = World { glm::dvec2 {0.0, 0.0}, glm::dvec2 {10.0, 10.0} };
        auto handle1 = world.add({
            BodyKind::DYNAMIC,
            Circle { glm::dvec2 {4.5, 5.0}, 1.0 }
        });
        auto handle2 = world.add({
            BodyKind::DYNAMIC,
            Circle { glm::dvec2 {5.5, 5.0}, 1.0 }
        });

        auto broad = world.broadphase();
        auto result = world.narrowphase(broad);

        expect(fatal(result.contains(NarrowCollisionPair {handle1, handle2, {}}))) << "Doesn't contain collision 0-1";
        auto collision0_1 = result.extract(NarrowCollisionPair {handle1, handle2, {}});
        expect(fatal(collision0_1.value().collision.has_value())) << "No collision information in 0-1";
        expect(1.0_d == collision0_1.value().collision->normal.x) << "Collision normal.x is not 1.0 in 0-1";
        expect(0.0_d == collision0_1.value().collision->normal.y) << "Collision normal.y is not 0.0 in 0-1";
        expect(1.0_d == collision0_1.value().collision->depth) << "Collision depth is not 1.0 in 0-1";

        expect(fatal(result.contains(NarrowCollisionPair {handle2, handle1, {}}))) << "Doesn't contain collision 1-0";
        auto collision1_0 = result.extract(NarrowCollisionPair {handle2, handle1, {}});
        expect(fatal(collision1_0.value().collision.has_value())) << "No collision information in 1-0";
        expect(-1.0_d == collision1_0.value().collision->normal.x) << "Collision normal.x is not -1.0 in 1-0";
        expect(0.0_d == collision1_0.value().collision->normal.y) << "Collision normal.y is not 0.0 in 1-0";
        expect(1.0_d == collision1_0.value().collision->depth) << "Collision depth is not 1.0 in 1-0";
    };
};
