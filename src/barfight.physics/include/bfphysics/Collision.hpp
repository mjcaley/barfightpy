#pragma once

#include <array>
#include <format>
#include <optional>
#include <ranges>
#include <vector>
#include <bfphysics/Circle.hpp>
#include <glm/glm.hpp>

#ifndef GLM_ENABLE_EXPERIMENTAL
#define GLM_ENABLE_EXPERIMENTAL
#endif
#include <glm/gtx/norm.hpp>

namespace barfight::physics {
    using barfight::physics::Circle;

    struct collision {
        glm::dvec2 normal;
        double depth;
    };

    auto resolution(auto shape1, auto shape2) -> std::optional<collision> {
        return {};
    }

    auto triple_product(glm::dvec2 a, glm::dvec2 b, glm::dvec2 c) -> glm::dvec2 {
        auto z = a.x * b.y - a.y * b.x;

        return { -c.y * z, c.x * z};
    }

    enum class SupportError {
        ZeroDirection
    };

    auto support(const auto& shape1, const auto& shape2, const glm::dvec2& direction) -> std::expected<glm::dvec2, SupportError> {
        auto furthest1 = shape1.furthest(direction);
        auto furthest2 = shape2.furthest(-direction);
        if (!furthest1 || !furthest2) {
            return std::unexpected(SupportError::ZeroDirection);
        }

        return *furthest1 - *furthest2;
    }

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

    auto colliding(const auto& shape1, const auto& shape2) -> std::optional<collision> {
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
                            return collision { glm::dvec2 {}, 0.0 }; // TODO: return collision from EPA
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

    auto colliding(const Circle& c1, const Circle& c2) -> std::optional<collision> {
        auto distance = glm::distance(c1.center, c2.center);
        auto overlap = c1.radius + c2.radius - distance;

        if (overlap > 0) {
            auto normal = glm::normalize(c2.center - c1.center);
            auto resolution_vector = normal;
            return collision { normal, overlap };
        }

        return {};
    }
}
