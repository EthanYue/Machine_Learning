from math import sqrt


def pearson(v1, v2):
	sum1 = sum(v1)
	sum2 = sum(v2)
	sum1Sq = sum([pow(v, 2) for v in v1])
	sum2Sq = sum([pow(v, 2) for v in v2])
	
	pSum = sum([v1[i]*v2[i] for i in range(len(v1))])
	num = pSum - (sum1*sum2/len(v1))
	den = sqrt((sum1Sq-pow(sum1, 2)/len(v1))*(sum2Sq-pow(sum2, 2)/len(v1)))
	if den == 0:
		return 0
	return 1.0-num/den


def hcluster(row, distance=pearson):
	distances = {}
	currentclusterid = -1
	clust = [bicluster(row[i], id=i) for i in range(len(row))]
	while len(clust) > 1:
		lowestpair = (0, 1)
		closest = distance(clust[0].vec, clust[1].vec)
		for i in range(len(clust)):
			for j in range(i+1, len(clust)):
				if (clust[i].id, clust[j].id) not in distances:
					distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)
				d = distances[(clust[i].id, clust[j].id)]
				if d < closest:
					closest = d
					lowestpair = (i, j)
	mergevec = [
		(clust[lowestpair[0].vec[i] + lowestpair[1].vec[i]]) / 2.0
	]


class bicluster:
	def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
		self.left = left
		self.right = right
		self.vec = vec
		self.id = id
		self.distance = distance
	
