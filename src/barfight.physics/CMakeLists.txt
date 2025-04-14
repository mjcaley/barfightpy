cmake_minimum_required(VERSION 4.0)

project(bf_physics LANGUAGES CXX)

set(CMAKE_CXX_SCAN_FOR_MODULES ON)

enable_testing()

include(cmake/CPM.cmake)

find_package(Python 3.13 COMPONENTS Interpreter Development.Module REQUIRED)

# if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
#   set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
#   set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
# endif()

# Detect the installed nanobind package and import it into CMake
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE nanobind_ROOT)
find_package(nanobind CONFIG REQUIRED)

CPMAddPackage("gh:g-truc/glm#1.0.1")
find_package(nanobind REQUIRED)

add_library(bfphysicslib STATIC)
target_sources(
  bfphysicslib
  PUBLIC
  FILE_SET CXX_MODULES
  FILES
    # Forward declarations
    lib/QuadTreeFwd.cppm

    # Basic types
    lib/BodyKind.cppm
    lib/BodyHandle.cppm
    lib/PrimitiveCommon.cppm
    lib/BoundingBox.cppm
    lib/Circle.cppm
    lib/OrientedRectangle.cppm
    lib/Polygon.cppm
    lib/Rectangle.cppm
    lib/BodyDescriptor.cppm

    lib/Shape.cppm
    lib/Collision.cppm
    lib/CollisionImpl.cppm
    lib/Body.cppm

    lib/QuadTree.cppm
    lib/QuadTreeNode.cppm
    lib/QuadTreeImpl.cppm

    lib/World.cppm

    lib/lib.cppm
)
target_compile_features(bfphysicslib PRIVATE cxx_std_23)
target_link_libraries(bfphysicslib PUBLIC glm::glm)

nanobind_add_module(bfphysics
    src/mod.cpp
)
set_property(TARGET bfphysics PROPERTY CXX_STANDARD 23)
target_link_libraries(bfphysics PRIVATE bfphysicslib)

CPMAddPackage("gh:boost-ext/ut@2.3.1")
add_executable(bfphysicstest)
target_compile_features(bfphysicstest PRIVATE cxx_std_23)
target_sources(bfphysicstest PRIVATE
    test/main.cpp
    test/primitives.cpp
    test/collision.cpp
    test/quadtree.cpp
    test/world.cpp
)
target_link_libraries(bfphysicstest PRIVATE Boost::ut bfphysicslib)
add_test(NAME tests COMMAND bfphysicstest)
