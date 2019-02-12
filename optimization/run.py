import optimization
import dorm
import social_network
# 航班问题
# domain = [(0, 7)] * (len(optimization.people) * 2)
# s = optimization.random_optimize(domain, optimization.schedule_cost)
# s = optimization.hill_climb(domain, optimization.schedule_cost)
# s = optimization.annealing_optimize(domain, optimization.schedule_cost)
# s = optimization.genetic_optimize(domain, optimization.schedule_cost)


# 分配问题
# dorm.print_sol([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
# s = optimization.random_optimize(dorm.domain, dorm.dorm_cost)
# s = optimization.genetic_optimize(dorm.domain, dorm.dorm_cost)


# 网络可视化
sol = optimization.random_optimize(social_network.domain, social_network.cross_count)
# s = optimization.annealing_optimize(social_network.domain, social_network.cross_count)
social_network.draw_network(sol)