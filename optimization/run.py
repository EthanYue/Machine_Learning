import optimization

domain = [(0, 7)] * (len(optimization.people) * 2)
# s = optimization.random_optimize(domain, optimization.schedule_cost)
# s = optimization.hill_climb(domain, optimization.schedule_cost)
# s = optimization.annealing_optimize(domain, optimization.schedule_cost)
s = optimization.genetic_optimize(domain, optimization.schedule_cost)
print(s)
optimization.print_schedule(s)

# print(res)
