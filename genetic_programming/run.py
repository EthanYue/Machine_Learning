import gp
# example_tree = gp.example_tree()
# example_tree.evaluate([5, 3])
# example_tree.display()

# random1 = gp.make_random_tree(2)
# random2 = gp.make_random_tree(2)
# print('random1 tree')
# random1.display()
# mutate = gp.mutate(random1, 2)
# print('mutate tree')
# mutate.display()
# print('random1 tree')
# random1.display()
# cross = gp.crossover(random1, random2)
# print('mutate tree')
# cross.display()

# res = random1.evaluate([2, 4])
# print(res)

# hidden_set = gp.build_hidden_set()
# res1 = gp.score_function(random1, hidden_set)
# res2 = gp.score_function(cross, hidden_set)
# print(res1)
# print(res2)

rf = gp.get_rank_function(gp.build_hidden_set())
gp.evolve(2, 500, rf)
