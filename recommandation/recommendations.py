from math import sqrt
critics = {
	'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
	              'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 'The Night Listener': 3.0},
	'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 'Just My Luck': 1.5,
	                 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5, 'The Night Listener': 3.0},
	'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
	                     'Superman Returns': 3.5, 'The Night Listener': 4.0},
	'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
	                 'Superman Returns': 4.0, 'You, Me and Dupree': 2.5, 'The Night Listener': 4.5},
	'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'Just My Luck': 2.0,
	                 'Superman Returns': 3.0, 'You, Me and Dupree': 2.0, 'The Night Listener': 3.0},
	'Jack Matthws': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
	                 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5, 'The Night Listener': 3.0},
	'Toby': {'Snakes on a Plane': 4.5, 'Superman Returns': 4.0, 'You, Me and Dupree': 1.0}
}


# p1与p2基于欧几里德距离的相似度
def sim_distance(prefs, person1, person2):
	si = {}
	for item in prefs[person1]:
		if item in prefs[person2]:
			si[item] = 1
	if len(si) == 0:
		return 0
	sum_of_squares = sum([pow(prefs[person1][item]-prefs[person2][item], 2) for item in prefs[person1] if item in prefs[person2]])
	return 1/(1+sqrt(sum_of_squares))


# p1与p2的皮尔逊系数
def sim_pearson(prefs, p1, p2):
	si = {}
	for item in prefs[p1]:
		if item in prefs[p2]:
			si[item] = 1
	n = len(si)
	if n == 0:
		return 1
	sum1 = sum([prefs[p1][it] for it in si])
	sum2 = sum([prefs[p2][it] for it in si])
	
	sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
	sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
	
	pSum = sum([prefs[p1][it]*prefs[p2][it] for it in si])
	
	num = pSum - (sum1 * sum2 / n)
	den = sqrt((sum1Sq-pow(sum1, 2)/n)*(sum2Sq-pow(sum2, 2)/n))
	if den == 0:
		return 0
	r = num / den
	return r


# 根据数据集返回某人的最为匹配者
def topMatches(prefs, person, n=5, similarity=sim_pearson):
	# 生成数据集中不同的人对应的分数和人名
	scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]
	res = sorted(scores, reverse=True)
	return res[0:n]


# 利用加权平均为某人提建议
def getRecommandations(prefs, person, similarity=sim_pearson):
	totals = {}
	simSums = {}
	for other in prefs:
		if other == person:
			continue
		sim = similarity(prefs, person, other)
		if sim <= 0:
			continue
		for item in prefs[other]:
			if item not in prefs[person] or prefs[person][item] == 0:
				totals.setdefault(item, 0)
				totals[item] += prefs[other][item] * sim
				simSums.setdefault(item, 0)
				simSums[item] += sim
	# 生成预测的评价分数和电影名称
	rankings = [(total/simSums[item], item) for item, total in totals.items()]
	res = sorted(rankings, reverse=True)
	return res


# 转换数据集格式
def transformPrefs(prefs):
	result = {}
	for person in prefs:
		for item in prefs[person]:
			result.setdefault(item, {})
			result[item][person] = prefs[person][item]
	return result


# 寻找最为相近的物品
def calSimilarItems(prefs, n=10):
	result = {}
	itemPrefs = transformPrefs(prefs)
	c = 0
	for item in itemPrefs:
		c += 1
		if c % 100 == 0:
			print("%d / %d" % (c, len(itemPrefs)))
		scores = topMatches(itemPrefs, item, n=n, similarity=sim_pearson)
		result[item] = scores
	return result


# 基于物品为某人给出推荐
def getRecommandedItems(prefs, itemMatch, user):
	userRatings = prefs[user]
	scores = {}
	totalSim = {}
	for item, rating in userRatings.items():
		for similarity, item2 in itemMatch[item]:
			if item2 in userRatings:
				continue
			scores.setdefault(item2, 0)
			scores[item2] += similarity * rating
			totalSim.setdefault(item2, 0)
			totalSim[item2] += similarity
	rankings = [(score/totalSim[item], item) for item, score in scores.items()]
	res = sorted(rankings, reverse=True)
	return res
