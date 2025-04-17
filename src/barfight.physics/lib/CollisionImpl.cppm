module;
#include <algorithm>
#include <array>
#include <cmath>
#include <expected>
#include <optional>
#include <ranges>
#include <variant>
#include <vector>
#include "spdlog/spdlog.h"
#include <glm/gtx/exterior_product.hpp>

export module barfight.physics:CollisionImpl;
import glm;

namespace barfight::physics {
    template<class... Ts>
    struct overloaded : Ts... { using Ts::operator()...; };

    template<class... Ts>
    overloaded(Ts...) -> overloaded<Ts...>;

    enum class SupportError {
        ZeroDirection
    };

    auto triple_product(glm::dvec2 a, glm::dvec2 b, glm::dvec2 c) -> glm::dvec2 {
        auto z = a.x * b.y - a.y * b.x;

        return { -c.y * z, c.x * z};
    }

    auto left_normal(const glm::dvec2& v) -> glm::dvec2 {
        return glm::normalize(glm::dvec2 { v.y, -v.x });
    }

    auto right_normal(const glm::dvec2& v) -> glm::dvec2 {
        return glm::normalize(glm::dvec2 { -v.y, v.x });
    }

    auto support(const auto& shape1, const auto& shape2, const glm::dvec2& direction) -> std::expected<glm::dvec2, SupportError>  {
        auto furthest1 = shape1.furthest(direction);
        auto furthest2 = shape2.furthest(-direction);
        if (!furthest1 || !furthest2) {
            return std::unexpected(SupportError::ZeroDirection);
        }

        return *furthest1 - *furthest2;
    }

#pragma region GJK

    export struct GJKThreeSimplex {
        glm::dvec2 a;
        glm::dvec2 b;
        glm::dvec2 c;
    };

    struct GJKTwoSimplex {
        glm::dvec2 a;
        glm::dvec2 b;
    };

    struct GJKOneSimplex {
        glm::dvec2 a;
    };

    struct GJKZeroSimplex {};

    using GJKSimplex = std::variant<GJKZeroSimplex, GJKOneSimplex, GJKTwoSimplex, GJKThreeSimplex>;

    auto gjk_add(GJKSimplex& simplex, const glm::dvec2 point) -> void {
        std::visit(overloaded{
            [&](const GJKZeroSimplex& arg) { simplex = GJKOneSimplex { point }; },
            [&](const GJKOneSimplex& arg) { simplex = GJKTwoSimplex { point, arg.a }; },
            [&](const GJKTwoSimplex& arg) { simplex = GJKThreeSimplex { point, arg.a, arg.b }; },
            [&](const GJKThreeSimplex& arg) { simplex = GJKThreeSimplex { point, arg.a, arg.b }; },
        }, simplex);
    }

    const auto gjk_max_iterations = 32;

    constexpr auto gjk_epsilon() -> double {
        auto epsilon = 0.5;
        while (1.0 + epsilon > 1.0) {
            epsilon *= 0.5;
        }

        return epsilon;
    }

    export auto gjk(const auto& shape1, const auto& shape2) -> std::optional<GJKThreeSimplex> {
        auto simplex = GJKSimplex { GJKZeroSimplex {} };
        auto direction = glm::normalize(shape1.get_vec2_position() - shape2.get_vec2_position());
        if (direction == glm::dvec2(0.0, 0.0)) {
            direction = glm::dvec2(1.0, 0.0);
        }
        auto support_point = support(shape1, shape2, direction);
        if (!support_point) { return {}; }
        gjk_add(simplex, support_point.value());

        if (glm::dot(std::get<GJKOneSimplex>(simplex).a, direction) <= 0.0) {
            return {};
        }

        direction = -direction;

        for (auto _ : std::ranges::views::iota(1, gjk_max_iterations)) {
            support_point = support(shape1, shape2, direction);
            if (!support_point) { return {}; }
            gjk_add(simplex, support_point.value());

            auto distance = glm::dot(support_point.value(), direction);
            if (glm::dot(support_point.value(), direction) <= gjk_epsilon()) {
                return {};
            }
            else {
                if (std::holds_alternative<GJKThreeSimplex>(simplex)) {
                    auto a = std::get<GJKThreeSimplex>(simplex).a;
                    auto b = std::get<GJKThreeSimplex>(simplex).b;
                    auto c = std::get<GJKThreeSimplex>(simplex).c;

                    auto ao = -a;
                    auto ab = b - a;
                    auto ac = c - a;

                    auto dot = ab.x * ac.y - ac.x * ab.y;
                    auto ac_perp = glm::dvec2 { -ac.y * dot, ac.x * dot };

                    auto ac_location = glm::dot(ac_perp, ao);
                    if (ac_location >= 0.0) {
                        simplex = GJKTwoSimplex { a, c };
                    }
                    else {
                        auto ab_perp = glm::dvec2 { ab.y * dot, -ab.x * dot };
                        auto ab_location = glm::dot(ab_perp, ao);
                        if (ab_location < 0.0) {
                            return std::get<GJKThreeSimplex>(simplex);
                        }
                        else {
                            simplex = GJKTwoSimplex { a, b };
                            direction = ab_perp;
                        }
                    }
                }
                else if (std::holds_alternative<GJKTwoSimplex>(simplex)) {
                    auto a = std::get<GJKTwoSimplex>(simplex).a;
                    auto b = std::get<GJKTwoSimplex>(simplex).b;

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

#pragma region EPA

    enum class EPAWindingDirection {
        unknown,
        clockwise,
        counter_clockwise
    };

    class EPAEdge {
        public:
        EPAEdge() {}
        EPAEdge(glm::dvec2 point1, glm::dvec2 point2, EPAWindingDirection winding)
            : point1(point1), point2(point2) {
                normal = point2 - point1;
                if (winding == EPAWindingDirection::clockwise) {
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

        auto operator <=>(const EPAEdge& other) const -> std::strong_ordering {
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

    auto get_winding(const GJKThreeSimplex& simplex) -> EPAWindingDirection {
        const auto& a = simplex.a;
        const auto& b = simplex.b;
        const auto& c = simplex.c;

        const auto ab = b - a;
        const auto ac = c - a;

        auto ab_cross = glm::cross(a, b);
        auto bc_cross = glm::cross(b, c);
        auto ca_cross = glm::cross(c, a);

        if (ab_cross > 0.0) {
            return EPAWindingDirection::clockwise;
        }
        else if (bc_cross > 0.0) {
            return EPAWindingDirection::counter_clockwise;
        }

        return EPAWindingDirection::unknown;
    }

    class EPAPolytope {
        public:
        EPAPolytope(const GJKThreeSimplex& simplex) {
            winding = get_winding(simplex);
            edges = {
                { simplex.c, simplex.b, winding },
                { simplex.b, simplex.a, winding },
                { simplex.a, simplex.b, winding }
            };
            std::make_heap(edges.begin(), edges.end(), std::greater<>{});
        }

        auto closest_edge() const -> const EPAEdge& {
            return edges.front();
        }

        auto expand(const glm::dvec2 point) -> void {
            std::pop_heap(edges.begin(), edges.end(), std::greater<>{});
            const auto& edge = edges.back();
            edges.pop_back();
            EPAEdge edge1 { edge.point1, point, winding };
            EPAEdge edge2 { point, edge.point2, winding };
            edges.push_back(edge1);
            std::push_heap(edges.begin(), edges.end(), std::greater<>{});
            edges.push_back(edge2);
            std::push_heap(edges.begin(), edges.end(), std::greater<>{});
        }

        private:
        std::vector<EPAEdge> edges {};
        EPAWindingDirection winding;
    };

    const int epa_max_iterations = 100;
    auto epa_epsilon = std::sqrt(gjk_epsilon());

    export struct EPAResult {
        glm::dvec2 normal;
        double depth;
    };

    export auto epa(const auto& shape1, const auto& shape2, const GJKThreeSimplex& simplex) -> EPAResult {
        auto polytope = EPAPolytope(simplex);
        EPAEdge edge;
        glm::dvec2 support_point;

        for (auto _ : std::views::iota(0, epa_max_iterations)) {
            edge = polytope.closest_edge();
            support_point = support(shape1, shape2, edge.normal).value();

            auto projection = glm::dot(support_point, edge.normal);
            if (projection - edge.distance < epa_epsilon) {
                return { edge.normal, edge.distance };
            }

            polytope.expand(support_point);
        }

        return { edge.normal, glm::dot(support_point, edge.normal) };
    }
}

#pragma endregion EPA
