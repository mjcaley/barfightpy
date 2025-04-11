cmake_minimum_required(VERSION 4.0)

project(bf_physics LANGUAGES CXX)

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

add_library(bfphysicslib STATIC
  lib/Circle.cpp
  lib/OrientedRectangle.cpp
  lib/Polygon.cpp
  lib/QuadTree.cpp
  lib/Rectangle.cpp
  lib/Collision.cpp
  lib/Collision.impl.cpp
  lib/Shape.cpp
  lib/World.cpp
)
set_property(TARGET bfphysicslib PROPERTY CXX_STANDARD 23)
target_include_directories(bfphysicslib PUBLIC include)
target_link_libraries(bfphysicslib PUBLIC glm::glm)

# add_library(bfphysicslib)
# set_property(TARGET bfphysicslib PROPERTY CXX_STANDARD 23)
# target_sources(
#   bfphysicslib
#   PUBLIC
#   FILE_SET CXX_MODULES
#   FILES
#     lib/lib.cppm
#     lib/BoundingBox.cppm
# )

add_library(bfphysicslib_module STATIC)
set_property(TARGET bfphysicslib_module PROPERTY CXX_STANDARD 23)
target_sources(
  bfphysicslib_module
  PUBLIC
  FILE_SET CXX_MODULES
  FILES
    newlib/lib.cppm
    newlib/PrimitiveCommon.cppm
    newlib/BoundingBox.cppm
    newlib/Circle.cppm
    newlib/OrientedRectangle.cppm
    newlib/Polygon.cppm
    newlib/Rectangle.cppm
    newlib/Shape.cppm
    newlib/BodyKind.cppm
    newlib/Collision.cppm
    newlib/CollisionImpl.cppm
    newlib/BodyDescriptor.cppm
    newlib/BodyHandle.cppm
    newlib/Body.cppm
    newlib/QuadTree.cppm
    newlib/QuadTreeNode.cppm
    newlib/QuadTreeChildren.cppm
    newlib/World.cppm
)
target_link_libraries(bfphysicslib_module PUBLIC glm::glm)

nanobind_add_module(bfphysics
    src/mod.cpp
)
set_property(TARGET bfphysics PROPERTY CXX_STANDARD 23)
target_link_libraries(bfphysics PRIVATE bfphysicslib_module)

CPMAddPackage("gh:boost-ext/ut@2.3.1")
add_executable(bfphysicstest)
set_property(TARGET bfphysicstest PROPERTY CXX_STANDARD 23)
set_property(TARGET bfphysicstest PROPERTY CMAKE_CXX_SCAN_FOR_MODULES 1)
target_compile_features(bfphysicstest PRIVATE cxx_std_23)
target_sources(bfphysicstest PRIVATE
    test/main.cpp
    test/primitives.cpp
    test/collision.cpp
)
target_link_libraries(bfphysicstest PRIVATE Boost::ut bfphysicslib_module)
add_test(NAME tests COMMAND bfphysicstest)
