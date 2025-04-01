cmake_minimum_required(VERSION 3.28)

project(bf_physics LANGUAGES CXX)

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
  lib/World.cpp
  lib/primitives/Circle.cpp
  lib/primitives/Rectangle.cpp
)
set_property(TARGET bfphysicslib PROPERTY CXX_STANDARD 23)
target_include_directories(bfphysicslib PUBLIC include)
target_link_libraries(bfphysicslib PUBLIC glm::glm)

nanobind_add_module(bfphysicsmod
    src/mod.cpp
)
set_property(TARGET bfphysicsmod PROPERTY CXX_STANDARD 23)
target_link_libraries(bfphysicsmod PRIVATE bfphysicslib)
