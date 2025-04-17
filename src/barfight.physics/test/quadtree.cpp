#include <boost/ut.hpp>

import barfight.physics;
import glm;

using namespace boost::ut;

suite<"quadtree"> quadtree = [] {
    using barfight::physics::QuadTreeNode;
    using barfight::physics::Body;
    using barfight::physics::BodyHandle;
    using barfight::physics::BodyKind;
    using barfight::physics::Shape;
    using barfight::physics::Circle;

    "quadtree properties set with defaults"_test = [] {
        std::vector<std::optional<Body>> bodies {};
        auto q = QuadTreeNode { {0.0, 0.0}, {10.0, 10.0}, bodies};

        expect(0.0_d == q.get_bounding_box().origin.x) << "origin.x is not 0.0";
        expect(0.0_d == q.get_bounding_box().origin.y) << "origin.y is not 0.0";
        expect(10.0_d == q.get_bounding_box().size.x) << "size.x is not 10.0";
        expect(10.0_d == q.get_bounding_box().size.y) << "size.y is not 10.0";
    };

    "quadtree bounding box fits in quadtree"_test = [] {
        auto bodies = std::vector<std::optional<Body>> {
            Body { BodyKind::DYNAMIC, Shape { Circle { glm::dvec2 {5.0, 5.0}, 1.0 } } },
            Body { BodyKind::DYNAMIC, Shape { Circle { glm::dvec2 {10.0, 5.0}, 1.0 } } }
        };
        auto q = QuadTreeNode { {0.0, 0.0}, {10.0, 10.0}, bodies};

        auto result_fits = q.fits(BodyHandle { 0 });
        expect(result_fits == true) << "Body doesn't fit in quadtree";

        auto result_doesnt_fit = q.fits(BodyHandle { 1 });
        expect(result_doesnt_fit == false) << "Body fits in quadtree when it shouldn't";
    };

    "quadtree adds body that's within bounds"_test = [] {
        auto bodies = std::vector<std::optional<Body>> {
            Body { BodyKind::DYNAMIC, Shape { Circle { glm::dvec2 {5.0, 5.0}, 1.0 } } }
        };
        auto q = QuadTreeNode { {0.0, 0.0}, {10.0, 10.0}, bodies};
        auto handle = BodyHandle { 0 };

        auto result = q.add(handle);

        expect(result == true);
    };

    "quadtree removes existing and non-existing bodies"_test = [] {
        auto bodies = std::vector<std::optional<Body>> {
            Body { BodyKind::DYNAMIC, Shape { Circle { glm::dvec2 {5.0, 5.0}, 1.0 } } }
        };
        auto q = QuadTreeNode { {0.0, 0.0}, {10.0, 10.0}, bodies};
        auto handle = BodyHandle { 0 };

        auto add_result = q.add(handle);
        q.remove(handle);
        q.remove(BodyHandle { 100 });

        expect(true);
    };

    "quadtree query returns bodies within bounds"_test = [] {
        auto bodies = std::vector<std::optional<Body>> {
            Body { BodyKind::DYNAMIC, Shape { Circle { glm::dvec2 {5.0, 5.0}, 1.0 } } }
        };
        auto q = QuadTreeNode { {0.0, 0.0}, {10.0, 10.0}, bodies};
        auto handle = BodyHandle { 0 };

        q.add(handle);
        auto found = q.query({{4.0, 4.0}, {6.0, 6.0}});

        expect(found.size() == 1) << "Number of bodies isn't 1";
    };
};
