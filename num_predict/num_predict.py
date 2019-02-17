from random import random, randint
import math


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
