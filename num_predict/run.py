import num_predict
from optimization import optimization

# res = num_predict.wine_price(95, 3)
# data = num_predict.wine_set1()
data = num_predict.wine_set2()
# s_data = num_predict.rescale(data, [10, 10, 0, 0.5])
# res2 = num_predict.euclidean(data[0]['input'], data[1]['input'])
# res = num_predict.knn_estimate(data, (95.0, 5.0), k=5)
# res = num_predict.weighted_knn(data, (95.0, 5.0))
# price = num_predict.wine_price(95.0, 5.0)
cost_func = num_predict.create_cost_func(num_predict.knn_estimate, data)
# scale = optimization.genetic_optimize(num_predict.weight_domain, cost_func, pop_size=5, max_iter=20)
# scale = optimization.annealing_optimize(num_predict.weight_domain, cost_func, step=2)
scale = optimization.random_optimize(num_predict.weight_domain, cost_func)
print(scale)
# res = num_predict.cross_validate(num_predict.weighted_knn, s_data)
# print(res)
