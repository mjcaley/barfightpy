#include <print>
#include <nanobind/nanobind.h>
#include <nanobind/stl/tuple.h>
#include <bfphysics/BodyKind.hpp>
#include <bfphysics/BodyHandle.hpp>
#include <bfphysics/World.hpp>
#include <bfphysics/Circle.hpp>
#include <bfphysics/Rectangle.hpp>
#include <bfphysics/Shape.hpp>

namespace nb = nanobind;
using namespace nb::literals;

NB_MODULE(bfphysics, m) {
    nb::module_ primitives = m.def_submodule("primitives");

    nb::class_<barfight::physics::Circle>(primitives, "Circle")
        .def(nb::init<std::tuple<double, double>, double>())
        .def_prop_rw(
            "center",
            [](barfight::physics::Circle& self) {
                return self.get_tuple_center();
            },
            [](barfight::physics::Circle& self, std::tuple<double, double> value) {
                self.set_tuple_center(value);
            })
        .def_prop_rw(
            "radius",
            [](barfight::physics::Circle& self) {
                return self.radius;
            },
            [](barfight::physics::Circle& self, double value) {
                self.radius = value;
            })
        .def_prop_rw(
            "position",
            [](barfight::physics::Circle& self) {
                return self.get_tuple_position();
            },
            [](barfight::physics::Circle& self, std::tuple<double, double> value) {
                self.set_tuple_position(value);
            });

    nb::class_<barfight::physics::Rectangle>(primitives, "Rectangle")
    .def(nb::init<std::tuple<double, double>, std::tuple<double, double>>())
        .def_prop_rw(
            "origin",
            [](barfight::physics::Rectangle& self) {
                return self.get_tuple_origin();
            },
            [](barfight::physics::Rectangle& self, std::tuple<double, double> value) {
                self.set_tuple_origin(value);
            })
        .def_prop_rw(
            "size",
            [](barfight::physics::Rectangle& self) {
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

    nb::class_<barfight::physics::Shape>(m, "Shape")
        .def(nb::init<barfight::physics::Circle>())
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

    nb::class_<barfight::physics::Body>(m, "Body");

    nb::class_<barfight::physics::BodyHandle>(m, "BodyHandle")
        .def_prop_ro("id_", [](const barfight::physics::BodyHandle& h) { return h.get_id(); });

    nb::class_<barfight::physics::World>(m, "World")
        .def(nb::init<>())
        .def(
            "add",
            [](barfight::physics::World& w, barfight::physics::BodyKind kind) {
                barfight::physics::BodyDescriptor desc = {
                    kind,
                    barfight::physics::Shape { barfight::physics::Circle { std::make_tuple(0.0, 0.0), 10.0 } }
                };

                return w.add(desc);
            },
            nb::arg("kind"))
        .def("remove", &barfight::physics::World::remove, "handle"_a)
        .def("clear", &barfight::physics::World::clear)
        ;
}
