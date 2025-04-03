#include <array>
#include <optional>
#include <ranges>
#include <vector>
#include <bfphysics/primitives/Circle.hpp>
#include <glm/glm.hpp>

namespace barfight::physics {
    using barfight::physics::primitives::Circle;

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

    // auto support(std::vector<glm::dvec2> vertices, glm::dvec2 direction) -> glm::dvec2 {
    //     auto furthest = std::ranges::max_element(
    //         vertices,
    //         [&direction](const auto& v1, const auto& v2) {
    //             return glm::dot(v1, direction) < glm::dot(v2, direction);
    //         });

    //     return *furthest;
    // }

    auto support(const auto& shape1, const auto& shape2, const glm::dvec2& direction) -> glm::dvec2 {
        return shape1.furthest(direction) - shape2.furthest(-direction);
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

    struct gjk_visitor {
        static auto add(const gjk_zero_simplex& simplex, const glm::dvec2 point) -> gjk_one_simplex {
            return { point };
        }

        static auto add(const gjk_one_simplex& simplex, const glm::dvec2 point) -> gjk_two_simplex {
            return { point, simplex.a };
        }

        static auto add(const gjk_two_simplex& simplex, const glm::dvec2 point) -> gjk_three_simplex {
            return { point, simplex.a, simplex.b };
        }

        static auto add(const gjk_three_simplex& simplex, const glm::dvec2 point) -> gjk_three_simplex {
            return { point, simplex.a, simplex.b };
        }
    };
    
    struct gjk_result_evolving {};
    struct gjk_result_not_found {};
    struct gjk_result_found {};

    using gjk_result = std::variant<gjk_result_evolving, gjk_result_not_found, gjk_result_found>;
    
    template<typename Shape1, typename Shape2>
    struct gjk {
        gjk(Shape1 shape1, Shape2 shape2) : shape1(shape1), shape2(shape2) {
            direction = glm::normalize(shape1.center - shape2.center);
            if (direction == glm::dvec2 { 0, 0 }) {
                direction = glm::dvec2 { 1, 0 };
            }
        }

        auto iterate() -> gjk_result {
            if (result) {
                return *result;
            }

            return iterate(simplex);
        }

        private:
        auto iterate(gjk_zero_simplex& simplex) -> gjk_result {
            simplex = gjk_one_simplex { support(shape1, shape2, direction) };
            if (glm::dot(std::get<gjk_one_simplex>(simplex).a, direction) <= 0.0) {
                return gjk_result_not_found {};
            }
            direction = -direction;

            return gjk_result_evolving {};
        }

        auto iterate(gjk_one_simplex& simplex) -> gjk_result {
            auto support_point = support(shape1, shape2, direction);
            simplex = gjk_visitor::add(simplex, support_point);

        }

        auto iterate(gjk_two_simplex& simplex) -> gjk_result {

        }

        auto iterate(gjk_three_simplex& simplex) -> gjk_result {

        }

        Shape1 shape1;
        Shape2 shape2;
        glm::dvec2 direction;
        std::optional<gjk_result> result {};
        std::variant<gjk_zero_simplex, gjk_one_simplex, gjk_two_simplex, gjk_three_simplex> simplex {};
    };

    // struct gjk_simplex {
    //     enum class simplex_case_kind {
    //         zero,
    //         one,
    //         two,
    //         three
    //     } simplex_case;

    //     auto get_simplex_case() const -> simplex_case_kind {
    //         return simplex_case;
    //     }

    //     auto push(const glm::dvec2 point) -> void {
    //         switch (simplex_case) {
    //             case simplex_case_kind::zero:
    //                 set_a(point);
    //                 break;
    //             case simplex_case_kind::one:
    //                 set_b(get_a());
    //                 set_a(point);
    //                 break;
    //             case simplex_case_kind::two:
    //             case simplex_case_kind::three:
    //                 set_c(get_b());
    //                 set_b(get_a());
    //                 set_a(point);
    //             break;
    //         }
    //     }

    //     auto last() const -> glm::dvec2 {
    //         return points.back();
    //     }

    //     auto get_a() const -> glm::dvec2 {
    //         return last();
    //     }

    //     auto set_a(glm::dvec2 point) -> void {
    //         points[2] = point;
    //     }

    //     auto get_b() const -> glm::dvec2 {
    //         return points[1];
    //     }

    //     auto remove_b() -> void {
    //         set_b(get_c());
    //         simplex_case = simplex_case_kind::two;
    //     }

    //     auto set_b(glm::dvec2 point) -> void {
    //         points[1] = point;
    //     }

    //     auto get_c() const -> glm::dvec2 {
    //         return points.front();
    //     }

    //     auto set_c(const glm::dvec2 point) -> void {
    //         points[0] = point;
    //     }

    //     private:
    //     simplex_case_kind simplex_case { simplex_case_kind::zero };
    //     std::array<glm::dvec2, 3> points {};
    // };

    const auto gjk_max_iterations = 32;

    constexpr auto gjk_epsilon() -> double {
        auto epsilon = 0.5;
        while (1.0 + epsilon > 1.0) {
            epsilon *= 0.5;
        }
        
        return epsilon;
    }

    auto colliding(const auto& shape1, const auto& shape2) -> std::optional<collision> {
        // // First point
        // gjk_simplex simplex {};
        // auto direction = glm::normalize(shape1.center - shape2.center);
        // if (direction == glm::dvec2 {0, 0})
        // {
        //     direction = glm::dvec2 {1, 0};
        // }
        // simplex = simplex.add(support(shape1, shape2, direction));


        // // Is it past the origin?
        // if (glm::dot(simplex.last(), direction) <= 0.0) {
        //     return {};
        // }

        // direction = -direction;

        // for (const auto _ : std::views::iota(64)) {
        //     const auto support_point = support(shape1, shape2, direction);
        //     simplex.push(support_point);

        //     if (glm::dot(support_point, direction) <= gjk_epsilon()) {
        //         return {};
        //     }

        //     const auto ao = -simplex.get_a();

        //     switch (simplex.simplex_case) {
        //         case gjk_simplex::simplex_case_kind::three:
        //         const auto ab = simplex.get_b() - simplex.get_a();
        //         const auto ac = simplex.get_c() - simplex.get_a();

        //         const auto dot = ab.x * ac.y - ac.x * ab.y;
        //         const auto ac_perp = glm::dvec2 { -ac.y * dot, ac.x * dot };

        //         const auto ac_location = glm::dot(ac_perp, ao);
        //         if (ac_location >= 0.0) {
        //             simplex.pop_last();
        //         }
        //         else {
        //             const auto ab_perp = glm::dvec2 { ab.y * dot, -ab.x * dot };
        //             const auto ab_location = ab_perp.dot(ao);
        //             if (ab_location < 0.0) {
        //                 return simplex;
        //             }
        //             else {
        //                 simplex.pop_first();
        //             }
        //         }
        //     }
        // }

        // return {};
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
