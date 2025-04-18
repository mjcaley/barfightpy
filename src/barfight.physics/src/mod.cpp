#include <print>
#include <nanobind/nanobind.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/variant.h>

import barfight.physics;

namespace nb = nanobind;
using namespace nb::literals;

NB_MODULE(bfphysics, m) {
#pragma region Primitives
    nb::module_ primitives = m.def_submodule("primitives");

    nb::class_<barfight::physics::Circle>(primitives, "Circle")
        .def(nb::init<std::tuple<double, double>, double>())
        .def_prop_rw(
            "center",
            [](const barfight::physics::Circle& self) {
                return self.get_tuple_center();
            },
            [](barfight::physics::Circle& self, std::tuple<double, double> value) {
                self.set_tuple_center(value);
            })
        .def_prop_rw(
            "radius",
            [](const barfight::physics::Circle& self) {
                return self.radius;
            },
            [](barfight::physics::Circle& self, double value) {
                self.radius = value;
            })
        .def_prop_rw(
            "position",
            [](const barfight::physics::Circle& self) {
                return self.get_tuple_position();
            },
            [](barfight::physics::Circle& self, std::tuple<double, double> value) {
                self.set_tuple_position(value);
            });

    nb::class_<barfight::physics::OrientedRectangle>(primitives, "OrientedRectangle")
        .def(nb::init<std::tuple<double, double>, std::tuple<double, double>, double>())
        .def_prop_rw(
            "center",
            [](const barfight::physics::OrientedRectangle& self) { return self.get_tuple_center(); },
            [](barfight::physics::OrientedRectangle & self, const std::tuple<double, double>& value) { self.set_tuple_center(value); }
        )
        .def_prop_rw(
            "half_extent",
            [](const barfight::physics::OrientedRectangle& self) {
                return self.get_tuple_half_extent();
            },
            [](barfight::physics::OrientedRectangle& self, std::tuple<double, double> value) {
                self.set_tuple_half_extent(value);
            })
        .def_prop_rw(
            "rotation",
            [](const barfight::physics::OrientedRectangle& self) {
                return self.rotation;
            },
            [](barfight::physics::OrientedRectangle& self, double value) {
                self.rotation = value;
            });

    nb::class_<barfight::physics::Polygon>(primitives, "Polygon")
        .def(nb::init<std::vector<std::tuple<double, double>>>())
        .def_prop_rw(
            "points",
            [](const barfight::physics::Polygon& self) { return self.get_tuple_points(); },
            [](barfight::physics::Polygon & self, std::vector<std::tuple<double, double>> value) { self.set_tuple_points(value); }
        )
        .def_prop_rw(
            "position",
            [](const barfight::physics::Polygon& self) {
                return self.get_tuple_position();
            },
            [](barfight::physics::Polygon& self, std::tuple<double, double> value) {
                self.set_tuple_position(value);
            });

    nb::class_<barfight::physics::Rectangle>(primitives, "Rectangle")
        .def(nb::init<std::tuple<double, double>, std::tuple<double, double>>())
        .def_prop_rw(
            "origin",
            [](const barfight::physics::Rectangle& self) {
                return self.get_tuple_origin();
            },
            [](barfight::physics::Rectangle& self, std::tuple<double, double> value) {
                self.set_tuple_origin(value);
            })
        .def_prop_rw(
            "size",
            [](const barfight::physics::Rectangle& self) {
                return self.get_tuple_size();
            },
            [](barfight::physics::Rectangle& self, std::tuple<double, double> value) {
                self.set_tuple_size(value);
            })
        .def_prop_rw(
            "position",
            [](const barfight::physics::Rectangle& self) {
                return self.get_tuple_position();
            },
            [](barfight::physics::Rectangle& self, std::tuple<double, double> value) {
                self.set_tuple_position(value);
            });
#pragma endregion Primitives

    nb::class_<barfight::physics::Shape>(m, "Shape")
        .def(nb::init<barfight::physics::Circle>())
        .def(nb::init<barfight::physics::OrientedRectangle>())
        .def(nb::init<barfight::physics::Polygon>())
        .def(nb::init<barfight::physics::Rectangle>())
        .def_prop_rw(
            "position",
            [](const barfight::physics::Shape& self) { return self.get_tuple_position(); },
            [](barfight::physics::Shape& self, std::tuple<double, double> value) { self.set_tuple_position(value); }
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

    nb::class_<barfight::physics::Body>(m, "Body");

    nb::class_<barfight::physics::BodyHandle>(m, "BodyHandle")
        .def_prop_ro("id_", [](const barfight::physics::BodyHandle& h) { return h.get_id(); });

    nb::class_<barfight::physics::World>(m, "World")
        .def(nb::init<std::tuple<double, double>, std::tuple<double, double>>())
        .def(
            "add",
            [](barfight::physics::World& w, const barfight::physics::BodyDescriptor& descriptor) {
                return w.add(descriptor);
            })
        .def("remove", &barfight::physics::World::remove, "handle"_a)
        .def("clear", &barfight::physics::World::clear);
}
