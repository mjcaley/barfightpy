#include <print>
#include <glm/glm.hpp>
#include <nanobind/nanobind.h>
#include <bfphysics/BodyKind.hpp>
#include <bfphysics/BodyHandle.hpp>
#include <bfphysics/World.hpp>

namespace nb = nanobind;

auto something() -> int {
    std::println("Hello world!");

    return 0;
}

NB_MODULE(bfphysics, m) {
    m.def("something", &something);

    nb::enum_<barfight::physics::BodyKind>(m, "BodyKind")
        .value("Static", barfight::physics::BodyKind::STATIC)
        .value("Dynamic", barfight::physics::BodyKind::DYNAMIC)
        .value("Sensor", barfight::physics::BodyKind::SENSOR);

    nb::class_<barfight::physics::World>(m, "World")
        .def(nb::init<>());
}
