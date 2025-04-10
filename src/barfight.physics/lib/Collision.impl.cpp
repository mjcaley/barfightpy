#include <bfphysics/Collision.impl.hpp>

auto barfight::physics::impl::triple_product(glm::dvec2 a, glm::dvec2 b, glm::dvec2 c) -> glm::dvec2 {
    auto z = a.x * b.y - a.y * b.x;

    return { -c.y * z, c.x * z};
}

// auto barfight::physics::impl::support(const auto& shape1, const auto& shape2, const glm::dvec2& direction) -> std::expected<glm::dvec2, SupportError> {
//     auto furthest1 = shape1.furthest(direction);
//     auto furthest2 = shape2.furthest(-direction);
//     if (!furthest1 || !furthest2) {
//         return std::unexpected(SupportError::ZeroDirection);
//     }

//     return *furthest1 - *furthest2;
// }

auto barfight::physics::impl::left_normal(const glm::dvec2& v) -> glm::dvec2 {
    return glm::normalize(glm::dvec2 { v.y, -v.x });
}

auto barfight::physics::impl::right_normal(const glm::dvec2& v) -> glm::dvec2 {
    return glm::normalize(glm::dvec2 { -v.y, v.x });
}

auto barfight::physics::impl::gjk_add(gjk_simplex& simplex, const glm::dvec2 point) -> void {
    std::visit(overloaded{
        [&](const gjk_zero_simplex& arg) { simplex = gjk_one_simplex { point }; },
        [&](const gjk_one_simplex& arg) { simplex = gjk_two_simplex { point, arg.a }; },
        [&](const gjk_two_simplex& arg) { simplex = gjk_three_simplex { point, arg.a, arg.b }; },
        [&](const gjk_three_simplex& arg) { simplex = gjk_three_simplex { point, arg.a, arg.b }; },
    }, simplex);
}

auto barfight::physics::impl::get_winding(const gjk_three_simplex& simplex) -> epa_winding_direction {
    const auto& a = simplex.a;
    const auto& b = simplex.b;
    const auto& c = simplex.c;

    const auto ab = b - a;
    const auto ac = c - a;

    auto ab_cross = glm::cross(a, b);
    auto bc_cross = glm::cross(b, c);
    auto ca_cross = glm::cross(c, a);

    if (ab_cross > 0.0) {
        return epa_winding_direction::clockwise;
    }
    else if (bc_cross > 0.0) {
        return epa_winding_direction::counter_clockwise;
    }

    return epa_winding_direction::unknown;
}
