#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <expected>
#include <optional>
#include <ranges>
#include <variant>
#include <vector>
#include <glm/glm.hpp>

#ifndef GLM_ENABLE_EXPERIMENTAL
#define GLM_ENABLE_EXPERIMENTAL
#endif
#include <glm/gtx/exterior_product.hpp>
#include <glm/gtx/norm.hpp>


namespace barfight::physics::impl {
    struct collision {
        glm::dvec2 normal;
        double depth;
    };

    enum class SupportError {
        ZeroDirection
    };

    auto triple_product(glm::dvec2 a, glm::dvec2 b, glm::dvec2 c) -> glm::dvec2 {
        auto z = a.x * b.y - a.y * b.x;

        return { -c.y * z, c.x * z};
    }

    auto support(const auto& shape1, const auto& shape2, const glm::dvec2& direction) -> std::expected<glm::dvec2, SupportError> {
        auto furthest1 = shape1.furthest(direction);
        auto furthest2 = shape2.furthest(-direction);
        if (!furthest1 || !furthest2) {
            return std::unexpected(SupportError::ZeroDirection);
        }

        return *furthest1 - *furthest2;
    }

    auto left_normal(const glm::dvec2& v) -> glm::dvec2 {
        return glm::normalize(glm::dvec2 { v.y, -v.x });
    }

    auto right_normal(const glm::dvec2& v) -> glm::dvec2 {
        return glm::normalize(glm::dvec2 { -v.y, v.x });
    }

    #pragma region GJK

    struct gjk_three_simplex {
        glm::dvec2 a;
        glm::dvec2 b;
        glm::dvec2 c;
    };

    struct gjk_two_simplex {
        glm::dvec2 a;
        glm::dvec2 b;
    };

    struct gjk_one_simplex {
        glm::dvec2 a;
    };

    struct gjk_zero_simplex {};

    using gjk_simplex = std::variant<gjk_zero_simplex, gjk_one_simplex, gjk_two_simplex, gjk_three_simplex>;

    struct gjk_result_evolving {};
    struct gjk_result_not_found {};
    struct gjk_result_found {};

    using gjk_result = std::variant<gjk_result_evolving, gjk_result_not_found, gjk_result_found>;

    auto gjk_add = [](auto&& arg, auto&& variant, const glm::dvec2 point) {
        gjk_simplex new_simplex;

        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, gjk_zero_simplex>) {
            new_simplex = gjk_one_simplex { point };
        }
        else if constexpr (std::is_same_v<T, gjk_one_simplex>) {
            new_simplex = gjk_two_simplex { point, arg.a };
        }
        else if constexpr (std::is_same_v<T, gjk_two_simplex>) {
            new_simplex = gjk_three_simplex { point, arg.a, arg.b };
        }
        else if constexpr (std::is_same_v<T, gjk_three_simplex>) {
            new_simplex = gjk_three_simplex { point, arg.a, arg.b };
        }
        else {
            static_assert(false, "non-exhaustive type");
        }

        variant.swap(new_simplex);
    };

    const auto gjk_max_iterations = 32;

    constexpr auto gjk_epsilon() -> double {
        auto epsilon = 0.5;
        while (1.0 + epsilon > 1.0) {
            epsilon *= 0.5;
        }

        return epsilon;
    }

    auto gjk(const auto& shape1, const auto& shape2) -> std::optional<gjk_three_simplex> {
        auto simplex = gjk_simplex { gjk_zero_simplex {} };
        auto direction = glm::normalize(shape1.get_center() - shape2.get_center());
        if (direction == glm::dvec2(0.0, 0.0)) {
            direction = glm::dvec2(1.0, 0.0);
        }
        auto support_point = support(shape1, shape2, direction);
        if (!support_point) { return {}; }
        std::visit([&](auto&& s) { gjk_add(s, simplex, support_point.value()); }, simplex);

        if (glm::dot(std::get<gjk_one_simplex>(simplex).a, direction) <= 0.0) {
            return {};
        }

        direction = -direction;

        for (auto _ : std::ranges::views::iota(1, gjk_max_iterations)) {
            support_point = support(shape1, shape2, direction);
            if (!support_point) { return {}; }
            std::visit([&](auto&& s) { gjk_add(s, simplex, support_point.value()); }, simplex);

            if (glm::dot(support_point.value(), direction) <= gjk_epsilon()) {
                return {};
            }
            else {
                if (std::holds_alternative<gjk_three_simplex>(simplex)) {
                    auto a = std::get<gjk_three_simplex>(simplex).a;
                    auto b = std::get<gjk_three_simplex>(simplex).b;
                    auto c = std::get<gjk_three_simplex>(simplex).c;

                    auto ao = -a;
                    auto ab = b - a;
                    auto ac = c - a;

                    auto dot = ab.x * ac.y - ac.x * ab.y;
                    auto ac_perp = glm::dvec2 { -ac.y * dot, ac.x * dot };

                    auto ac_location = glm::dot(ac_perp, ao);
                    if (ac_location >= 0.0) {
                        simplex = gjk_two_simplex { a, c };
                    }
                    else {
                        auto ab_perp = glm::dvec2 { ab.y * dot, -ab.x * dot };
                        auto ab_location = glm::dot(ab_perp, ao);
                        if (ab_location < 0.0) {
                            return std::get<gjk_three_simplex>(simplex);
                        }
                        else {
                            simplex = gjk_two_simplex { a, b };
                            direction = ab_perp;
                        }
                    }
                }
                else if (std::holds_alternative<gjk_two_simplex>(simplex)) {
                    auto a = std::get<gjk_two_simplex>(simplex).a;
                    auto b = std::get<gjk_two_simplex>(simplex).b;

                    auto ao = -a;
                    auto ab = b - a;

                    direction = triple_product(ab, ao, ab);
                    if (glm::length2(direction) <= gjk_epsilon()) {
                        direction = glm::dvec2 { direction.y, -direction.x }; // left normal
                    }
                }
            }
        }

        return {};
    }

    #pragma endregion GJK


    enum class epa_winding_direction {
        unknown,
        clockwise,
        counter_clockwise
    };

    class epa_edge {
        public:
        epa_edge() {}
        epa_edge(glm::dvec2 point1, glm::dvec2 point2, epa_winding_direction winding)
            : point1(point1), point2(point2) {
                normal = point2 - point1;
                if (winding == epa_winding_direction::clockwise) {
                    normal = right_normal(normal);
                }
                else {
                    normal = left_normal(normal);
                }

                distance = std::abs(point1.x * normal.x + point1.y * normal.y);
        }

        glm::dvec2 point1;
        glm::dvec2 point2;
        glm::dvec2 normal;
        double distance;

        auto operator <=>(const epa_edge& other) const -> std::strong_ordering {
            if (distance < other.distance) {
                return std::strong_ordering::less;
            }
            else if (distance > other.distance) {
                return std::strong_ordering::greater;
            }
            else {
                return std::strong_ordering::equal;
            }
        }
    };

    auto get_winding(const gjk_three_simplex& simplex) -> epa_winding_direction {
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

    class epa_polytope {
        public:
        epa_polytope(const gjk_three_simplex& simplex) {
            winding = get_winding(simplex);
            edges = {
                { simplex.c, simplex.b, winding },
                { simplex.b, simplex.a, winding },
                { simplex.a, simplex.b, winding }
            };
            std::make_heap(edges.begin(), edges.end(), std::greater<>{});
        }

        auto closest_edge() const -> const epa_edge& {
            return edges.front();
        }

        auto expand(const glm::dvec2 point) -> void {
            std::pop_heap(edges.begin(), edges.end(), std::greater<>{});
            auto edge = edges.back();
            edges.pop_back();
            epa_edge edge1 { edge.point1, point, winding };
            epa_edge edge2 { point, edge.point2, winding };
            edges.push_back(edge1);
            std::push_heap(edges.begin(), edges.end(), std::greater<>{});
            edges.push_back(edge2);
            std::push_heap(edges.begin(), edges.end(), std::greater<>{});
        }

        private:
        std::vector<epa_edge> edges {};
        epa_winding_direction winding;
    };

    const int epa_max_iterations = 100;
    constexpr auto epa_epsilon() -> double {
        return std::sqrt(gjk_epsilon());
    }

    auto epa(const auto& shape1, const auto& shape2, const gjk_three_simplex& simplex) -> collision {
        auto polytope = epa_polytope(simplex);
        epa_edge edge;
        glm::dvec2 support_point;

        for (auto _ : std::views::iota(0, epa_max_iterations)) {
            edge = polytope.closest_edge();
            support_point = support(shape1, shape2, edge.normal).value();

            auto projection = glm::dot(support_point, edge.normal);
            if (projection - edge.distance < epa_epsilon()) {
                return { edge.normal, edge.distance };
            }

            polytope.expand(support_point);
        }

        return { edge.normal, glm::dot(support_point, edge.normal) };
    }
}
