#include <print>
#include <ranges>
#include <nanobind/nanobind.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/variant.h>

import barfight.physics;
import glm;

namespace nb = nanobind;
using namespace nb::literals;

auto to_tuple(const glm::dvec2& v) -> std::tuple<double, double> {
    return std::make_tuple(v.x, v.y);
}

auto to_vec2(const std::tuple<double, double>& t) -> glm::dvec2 {
    return glm::dvec2 { std::get<0>(t), std::get<1>(t) };
}

NB_MODULE(bfphysics, m) {
#pragma region Primitives
    nb::module_ primitives = m.def_submodule("primitives");

    nb::class_<barfight::physics::Circle>(primitives, "Circle")
        .def("__init__", [](barfight::physics::Circle* self, const std::tuple<double, double> center, const double radius) {
            new (self) barfight::physics::Circle { to_vec2(center), radius };
        })
        .def_prop_rw(
            "center",
            [](const barfight::physics::Circle& self) {
                return to_tuple(self.center);
            },
            [](barfight::physics::Circle& self, std::tuple<double, double> value) {
                self.center = to_vec2(value);
            })
        .def_prop_rw(
            "radius",
            [](const barfight::physics::Circle& self) {
                return self.radius;
            },
            [](barfight::physics::Circle& self, const double value) {
                self.radius = value;
            })
        .def_prop_rw(
            "position",
            [](const barfight::physics::Circle& self) {
                return to_tuple(self.get_position());
            },
            [](barfight::physics::Circle& self, const std::tuple<double, double> value) {
                self.set_position(to_vec2(value));
            });

    nb::class_<barfight::physics::OrientedRectangle>(primitives, "OrientedRectangle")
        .def("__init__", [](
            barfight::physics::OrientedRectangle* self,
            const std::tuple<double, double> center,
            const std::tuple<double, double> half_extent,
            const double rotation) {
            new (self) barfight::physics::OrientedRectangle { to_vec2(center), to_vec2(half_extent), rotation };
        })
        .def_prop_rw(
            "center",
            [](const barfight::physics::OrientedRectangle& self) { return to_tuple(self.center); },
            [](barfight::physics::OrientedRectangle& self, const std::tuple<double, double>& value) { self.center = to_vec2(value); }
        )
        .def_prop_rw(
            "half_extent",
            [](const barfight::physics::OrientedRectangle& self) {
                return to_tuple(self.half_extent);
            },
            [](barfight::physics::OrientedRectangle& self, const std::tuple<double, double> value) {
                self.half_extent = to_vec2(value);
            })
        .def_prop_rw(
            "rotation",
            [](const barfight::physics::OrientedRectangle& self) {
                return self.rotation;
            },
            [](barfight::physics::OrientedRectangle& self, const double value) {
                self.rotation = value;
            });

    nb::class_<barfight::physics::Polygon>(primitives, "Polygon")
        .def("__init__", [](
            barfight::physics::Polygon* self,
            const std::vector<std::tuple<double, double>> points) {
            const auto vec2_points = points
            | std::views::transform([](auto&& point) { return to_vec2(point); })
            | std::ranges::to<std::vector<glm::dvec2>>();
            new (self) barfight::physics::Polygon { vec2_points };
        })
        .def_prop_rw(
            "points",
            [](const barfight::physics::Polygon& self) {
                return self.points
                | std::views::transform([] (auto&& point) {
                    return to_tuple(point);
                })
                | std::ranges::to<std::vector<std::tuple<double, double>>>();
            },
            [](barfight::physics::Polygon& self, std::vector<std::tuple<double, double>> value) {
                auto points = value
                | std::views::transform([] (auto&& point) {
                    return to_vec2(point);
                })
                | std::ranges::to<std::vector<glm::dvec2>>();
                self.points = points;
            }
        )
        .def_prop_rw(
            "position",
            [](const barfight::physics::Polygon& self) {
                return to_tuple(self.get_position());
            },
            [](barfight::physics::Polygon& self, const std::tuple<double, double> value) {
                self.set_position(to_vec2(value));
            });

    nb::class_<barfight::physics::Rectangle>(primitives, "Rectangle")
        .def("__init__", [](
            barfight::physics::Rectangle* self,
            const std::tuple<double, double> origin,
            const std::tuple<double, double> size) {
            new (self) barfight::physics::Rectangle { to_vec2(origin), to_vec2(size) };
        })
        .def_prop_rw(
            "origin",
            [](const barfight::physics::Rectangle& self) {
                return to_tuple(self.origin);
            },
            [](barfight::physics::Rectangle& self, const std::tuple<double, double> value) {
                self.origin = to_vec2(value);
            })
        .def_prop_rw(
            "size",
            [](const barfight::physics::Rectangle& self) {
                return to_tuple(self.size);
            },
            [](barfight::physics::Rectangle& self, const std::tuple<double, double> value) {
                self.size = to_vec2(value);
            })
        .def_prop_rw(
            "position",
            [](const barfight::physics::Rectangle& self) {
                return to_tuple(self.get_position());
            },
            [](barfight::physics::Rectangle& self, const std::tuple<double, double> value) {
                self.set_position(to_vec2(value));
            });
#pragma endregion Primitives

    nb::class_<barfight::physics::BoundingBox>(m, "BoundingBox")
        .def(nb::init<barfight::physics::BoundingBox>())
        .def("__init__", [](barfight::physics::BoundingBox* t, const std::tuple<double, double> origin, const std::tuple<double, double> size) {
            new (t) barfight::physics::BoundingBox { to_vec2(origin), to_vec2(size) };
        })
        .def_prop_rw(
            "origin",
            [](const barfight::physics::BoundingBox& self) {
                return to_tuple(self.origin);
            },
            [](barfight::physics::BoundingBox& self, const std::tuple<double, double> value) {
                self.origin = to_vec2(value);
            })
        .def_prop_rw(
            "size",
            [](const barfight::physics::BoundingBox& self) {
                return to_tuple(self.size);
            },
            [](barfight::physics::BoundingBox& self, const std::tuple<double, double> value) {
                self.size = to_vec2(value);
            });

    nb::class_<barfight::physics::Shape>(m, "Shape")
        .def(nb::init<barfight::physics::Circle>())
        .def(nb::init<barfight::physics::OrientedRectangle>())
        .def(nb::init<barfight::physics::Polygon>())
        .def(nb::init<barfight::physics::Rectangle>())
        .def_prop_rw(
            "position",
            [](const barfight::physics::Shape& self) { return to_tuple(self.get_position()); },
            [](barfight::physics::Shape& self, const std::tuple<double, double> value) { self.set_position(to_vec2(value)); }
        );

    nb::enum_<barfight::physics::BodyKind>(m, "BodyKind")
        .value("Static", barfight::physics::BodyKind::STATIC)
        .value("Dynamic", barfight::physics::BodyKind::DYNAMIC)
        .value("Sensor", barfight::physics::BodyKind::SENSOR);

    nb::class_<barfight::physics::BodyDescriptor>(m, "BodyDescriptor")
        .def(nb::init<barfight::physics::BodyKind, barfight::physics::Circle>())
        .def(nb::init<barfight::physics::BodyKind, barfight::physics::OrientedRectangle>())
        .def(nb::init<barfight::physics::BodyKind, barfight::physics::Polygon>())
        .def(nb::init<barfight::physics::BodyKind, barfight::physics::Rectangle>())
        .def_prop_ro("kind", [](const barfight::physics::BodyDescriptor& self) { return self.kind; })
        .def_prop_ro("shape", [](const barfight::physics::BodyDescriptor& self) { return self.shape; });

    nb::class_<barfight::physics::Body>(m, "Body")
        .def_prop_rw(
            "kind",
            [](const barfight::physics::Body& self) { return self.kind; },
            [](barfight::physics::Body& self, barfight::physics::BodyKind value) { self.kind = value; }
        )
        .def_prop_rw("shape",
            [](const barfight::physics::Body& self) { return self.shape.get_shape(); },
            [](barfight::physics::Body& self, const barfight::physics::Shape& value) { self.shape = value; }
        )
        ;

    nb::class_<barfight::physics::BodyHandle>(m, "BodyHandle")
        .def_prop_ro("id_", &barfight::physics::BodyHandle::get_id);

    nb::class_<barfight::physics::World>(m, "World")
        .def("__init__", [](
            barfight::physics::World* self,
            const std::tuple<double, double> origin,
            const std::tuple<double, double> size) {
            new (self) barfight::physics::World { to_vec2(origin), to_vec2(size) };
        })
        .def("add", &barfight::physics::World::add, "descriptor"_a)
        .def("remove", &barfight::physics::World::remove, "handle"_a)
        .def("clear", &barfight::physics::World::clear)
        .def("get", &barfight::physics::World::get, "handle"_a, nb::rv_policy::reference);
}
