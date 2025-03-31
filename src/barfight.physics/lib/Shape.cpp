#include <bfphysics/Shape.hpp>
#include <glm/vec2.hpp>

auto barfight::physics::Shape::get_position() const -> glm::bvec2 {
    return std::visit([](auto& s) { return s.get_position(); }, shape);
}

auto barfight::physics::Shape::set_position(const glm::bvec2& position) {
    std::visit([position](auto& s) { s.set_position(position); }, shape);
}

auto barfight::physics::Shape::furthest(glm::dvec2 direction) const -> glm::bvec2 {

}

