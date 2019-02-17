import num_predict


# res = num_predict.wine_price(95, 3)
data = num_predict.wine_set1()
# res2 = num_predict.euclidean(data[0]['input'], data[1]['input'])
res = num_predict.knn_estimate(data, (95.0, 5.0), k=10)
price = num_predict.wine_price(95.0, 5.0)
print(res)
print(price)
