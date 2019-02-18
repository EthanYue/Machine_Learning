from random import random, randint
import math

weight_domain = [(0, 20)] * 4


def wine_price(rating, age):
	peak_age = rating - 50
	price = rating / 2
	if age > peak_age:
		# 经过峰值年，后继五年价格会贬低
		price = price * (5 - (age - peak_age))
	else:
		# 价格在接近峰值年时会增加到原值的五倍
		price = price * (5 * ((age + 1) / peak_age))
	if price < 0:
		price = 0
	return price


def wine_set1():
	rows = []
	for i in range(300):
		rating = random() * 50 + 50
		age = random() * 50
		price = wine_price(rating, age)
		price *= (random() * 0.4 + 0.8)
		rows.append({'input': (rating, age), 'result': price})
	return rows


def wine_set2():
	rows = []
	for i in range(300):
		rating = random() * 50 + 50
		age = random() * 50
		aisle = float(randint(1, 20))
		bottle_size = [375.0, 750.0, 1500.0, 3000.0][randint(0, 3)]
		price = wine_price(rating, age)
		price *= (bottle_size / 750)
		price *= (random() * 0.9 + 0.2)
		rows.append({'input': (rating, age, aisle, bottle_size), 'result': price})
	return rows


# 将不同变量按比例缩放
def rescale(data, scale):
	scaled_data = []
	for row in data:
		scaled = [scale[i] * row['input'][i] for i in range(len(scale))]
		scaled_data.append({'input': scaled, 'result': row['result']})
	return scaled_data

def euclidean(v1, v2):
	d = 0.0
	for i in range(len(v1)):
		d += (v1[i] - v2[i]) ** 2
	return math.sqrt(d)


def get_distances(data, vec1):
	distance_list = []
	for i in range(len(data)):
		vec2 = data[i]['input']
		distance_list.append((euclidean(vec1, vec2), i))
	distance_list.sort()
	return distance_list


def knn_estimate(data, vec1, k=5):
	d_list = get_distances(data, vec1)
	avg = 0.0
	# 对前k项结果求平均
	for i in range(k):
		idx = d_list[i][1]
		avg += data[idx]['result']
	avg = avg / k
	return avg


# 反函数
def inverse_weight(dist, num=1.0, const=0.1):
	return num / (dist + const)


# 减法函数
def subtract_weight(dist, const=1.0):
	if dist > const:
		return 0
	return const - dist


# 高斯函数
def gaussian(dist, sigma=10.0):
	return math.e ** (-dist ** 2 / (2 * sigma ** 2))


# 加权k邻近算法
def weighted_knn(data, vec1, k=5, weight_func=gaussian):
	d_list = get_distances(data, vec1)
	avg = 0.0
	total_weight = 0.0
	for i in range(k):
		dist = d_list[i][0]
		idx = d_list[i][1]
		weight = weight_func(dist)
		avg += weight * data[idx]['result']
		total_weight += weight
	avg = avg / total_weight
	return avg


# 将数据分为测试机和训练集
def divide_data(data, test=0.05):
	train_set = []
	test_set = []
	for row in data:
		if random() < test:
			test_set.append(row)
		else:
			train_set.append(row)
	return train_set, test_set


# 评估训练集和测试集的结果差异
def test_algorithm(alg_func, train_set, test_set):
	error = 0.0
	for row in test_set:
		guess = alg_func(train_set, row['input'])
		error += (row['result'] - guess) ** 2
	return error/len(test_set)


# 交叉验证
def cross_validate(alg_func, data, trials=100, test=0.05):
	error = 0.0
	for i in range(trials):
		train_set, test_set = divide_data(data, test)
		error += test_algorithm(alg_func, train_set, test_set)
	return error / trials


# 定义成本函数，计算不同比例的交叉验证的误差
def create_cost_func(alg_func, data):
	def cost_func(scale):
		s_data = rescale(data, scale)
		return cross_validate(alg_func, s_data, trials=10)
	return cost_func

