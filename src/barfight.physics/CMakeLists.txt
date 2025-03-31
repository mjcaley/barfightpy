cmake_minimum_required(VERSION 4.0)

project(bf_physics)

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

nanobind_add_module(bfphysics
    lib/lib.cpp
    lib/World.cpp
    lib/primitives/Circle.cpp
)
set_property(TARGET bfphysics PROPERTY CXX_STANDARD 23)
target_include_directories(bfphysics PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include/)
target_link_libraries(bfphysics PRIVATE glm::glm)
