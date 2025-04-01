#include <print>
#include <glm/glm.hpp>
#include <nanobind/nanobind.h>
#include <nanobind/stl/tuple.h>
#include <bfphysics/BodyKind.hpp>
#include <bfphysics/BodyHandle.hpp>
#include <bfphysics/World.hpp>
#include <bfphysics/primitives/Circle.hpp>
#include <bfphysics/primitives/Rectangle.hpp>

namespace nb = nanobind;
using namespace nb::literals;

NB_MODULE(bfphysics, m) {
    nb::module_ primitives = m.def_submodule("primitives");

    nb::class_<barfight::physics::primitives::Circle>(primitives, "Circle")
        .def("__init__", [](barfight::physics::primitives::Circle* self, std::tuple<nb::float_, nb::float_> center, nb::float_ radius) {
            auto center_arg = glm::bvec2 { static_cast<double>(std::get<0>(center)), static_cast<double>(std::get<1>(center)) };
            auto radius_arg = static_cast<double>(radius);
            new (self) barfight::physics::primitives::Circle(center_arg, radius_arg);
        })
        .def_prop_rw(
            "center",
            [](barfight::physics::primitives::Circle& self) {
                return nb::make_tuple(self.center.x, self.center.y);
            },
            [](barfight::physics::primitives::Circle& self, std::tuple<nb::float_, nb::float_> value) {
                auto center_arg = glm::bvec2 { static_cast<double>(std::get<0>(value)), static_cast<double>(std::get<1>(value)) };
                self.center = center_arg;
            })
        .def_prop_rw(
            "radius",
            [](barfight::physics::primitives::Circle& self) {
                return self.radius;
            },
            [](barfight::physics::primitives::Circle& self, nb::float_ value) {
                self.radius = static_cast<double>(value);
            })
        .def_prop_rw(
            "position",
            [](barfight::physics::primitives::Circle& self) {
                // auto position = self.get_tuple_position();
                // return nb::make_tuple(position.x, position.y);
                return self.get_tuple_position();
            },
            [](barfight::physics::primitives::Circle& self, std::tuple<nb::float_, nb::float_> value) {
                auto position_arg = glm::bvec2 { static_cast<double>(std::get<0>(value)), static_cast<double>(std::get<1>(value)) };
                self.set_tuple_position(position_arg);
            })
        .def(
            "furthest",
            [](barfight::physics::primitives::Circle& self, std::tuple<nb::float_, nb::float_> direction) {
                auto direction_arg = glm::bvec2 { static_cast<double>(std::get<0>(direction)), static_cast<double>(std::get<1>(direction)) };
                auto point = self.furthest_tuple(direction_arg);

                if (!point) {
                    throw std::invalid_argument { "Cannot give a zero vector as a direction" };
                }

                return nb::make_tuple(point->x, point->y);
            }
        );

    nb::class_<barfight::physics::primitives::Rectangle>(primitives, "Rectangle")
        .def("__init__", [](barfight::physics::primitives::Rectangle* self, std::tuple<nb::float_, nb::float_> origin, std::tuple<nb::float_, nb::float_> size) {
            auto origin_arg = glm::bvec2 { static_cast<double>(std::get<0>(origin)), static_cast<double>(std::get<1>(origin)) };
            auto size_arg = glm::bvec2 { static_cast<double>(std::get<0>(origin)), static_cast<double>(std::get<1>(origin)) };
            new (self) barfight::physics::primitives::Rectangle(origin_arg, size_arg);
        })
        .def_prop_rw(
            "origin",
            [](barfight::physics::primitives::Rectangle& self) {
                return nb::make_tuple(self.origin.x, self.origin.y);
            },
            [](barfight::physics::primitives::Rectangle& self, std::tuple<nb::float_, nb::float_> value) {
                auto origin_arg = glm::bvec2 { static_cast<double>(std::get<0>(value)), static_cast<double>(std::get<1>(value)) };
                self.origin = origin_arg;
            })
        .def_prop_rw(
            "size",
            [](barfight::physics::primitives::Rectangle& self) {
                return nb::make_tuple(self.size.x, self.size.y);
            },
            [](barfight::physics::primitives::Rectangle& self, std::tuple<nb::float_, nb::float_> value) {
                auto size_arg = glm::bvec2 { static_cast<double>(std::get<0>(value)), static_cast<double>(std::get<1>(value)) };
                self.size = size_arg;
            })
        .def_prop_rw(
            "position",
            [](barfight::physics::primitives::Rectangle& self) {
                auto position = self.get_position();
                return nb::make_tuple(position.x, position.y);
            },
            [](barfight::physics::primitives::Rectangle& self, std::tuple<nb::float_, nb::float_> value) {
                auto position_arg = glm::bvec2 { static_cast<double>(std::get<0>(value)), static_cast<double>(std::get<1>(value)) };
                self.set_position(position_arg);
            })
        .def(
            "furthest",
            [](barfight::physics::primitives::Rectangle& self, std::tuple<nb::float_, nb::float_> direction) {
                auto direction_arg = glm::bvec2 { static_cast<double>(std::get<0>(direction)), static_cast<double>(std::get<1>(direction)) };
                auto point = self.furthest(direction_arg);

                if (!point) {
                    throw std::invalid_argument { "Cannot give a zero vector as a direction" };
                }

                return nb::make_tuple(point->x, point->y);
            }
        );

    nb::enum_<barfight::physics::BodyKind>(m, "BodyKind")
        .value("Static", barfight::physics::BodyKind::STATIC)
        .value("Dynamic", barfight::physics::BodyKind::DYNAMIC)
        .value("Sensor", barfight::physics::BodyKind::SENSOR);

    // nb::class_<barfight::physics::Body>(m, "Body")

    // nb::class_<barfight::physics::primitives::Circle>(m, );


    nb::class_<barfight::physics::BodyHandle>(m, "BodyHandle")
        .def_prop_ro("id_", [](barfight::physics::BodyHandle& h) { return h.get_id(); });

    nb::class_<barfight::physics::World>(m, "World")
        .def(nb::init<>())
        .def(
            "add",
            [](barfight::physics::World& w, barfight::physics::BodyKind kind) {
                barfight::physics::BodyDescriptor desc = {
                    kind,
                    barfight::physics::Shape { barfight::physics::primitives::Circle { glm::bvec2 {0.0, 0.0}, 10.0 } }
                };

                return w.add(desc);
            },
            nb::arg("kind"))
        .def("remove", &barfight::physics::World::remove, "handle"_a)
        .def("clear", &barfight::physics::World::clear)
        ;
}
