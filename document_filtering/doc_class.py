import re
import math


def sample_train(_class):
	_class.train('Nobody owns the water.', 'good')
	_class.train('the quick rabbit jumps fences', 'good')
	_class.train('buy pharmaceuticals now', 'bad')
	_class.train('make quick money at the online casino', 'bad')
	_class.train('the quick brown fox jumps', 'good')


def get_words(doc):
	splitter = re.compile(r'\W')
	words = [s.lower() for s in splitter.split(doc) if len(s) > 2 and len(s) < 20]
	return dict([(w, 1) for w in words])


class classifier:
	def __init__(self, get_features, file_name=None):
		"""
		:param get_features: 提取特征函数，例如get_words()
		:param file_name:
		"""
		# 统计特征/分类组合的数量
		self.f_c = {}
		# 统计每个分类中的文档数量
		self.c_c = {}
		self.get_features = get_features
	
	# 增加对特征/分类组合的计数值
	def inc_f(self, f, cat):
		self.f_c.setdefault(f, {})
		self.f_c[f].setdefault(cat, 0)
		self.f_c[f][cat] += 1
	
	# 增加对某一分类的计数值
	def inc_c(self, cat):
		self.c_c.setdefault(cat, 0)
		self.c_c[cat] += 1
	
	# 某一分类特征出现于某一分类中的次数
	def f_count(self, f, cat):
		if f in self.f_c and cat in self.f_c[f]:
			return float(self.f_c[f][cat])
		return 0.0
	
	# 属于某一分类的内容项数量
	def c_count(self, cat):
		if cat in self.c_c:
			return float(self.c_c[cat])
		return 0
	
	# 所有内容项的数量
	def total_count(self):
		return sum(self.c_c.values())
	
	# 所有分类的列表
	def categories(self):
		return self.c_c.keys()
	
	def train(self, item, cat):
		features = self.get_features(item)
		# 给每个分类增加计数值
		for f in features:
			self.inc_f(f, cat)
		self.inc_c(cat)
	
	def f_prob(self, f, cat):
		if self.c_count(cat) == 0:
			return 0
		# 特征在分类中出现的总次数，除以分类中包含内容项的总数
		return self.f_count(f, cat) / self.c_count(cat)
	
	def weighted_prob(self, f, cat, pr_func, weight=1, average_p=0.5):
		"""
		:param f:
		:param cat:
		:param pr_func: 计算概率值的函数， 当前为f_prob()
		:param weight:
		:param average_p: 平均初始概率为0.5
		:return:
		"""
		basic_prob = pr_func(f, cat)
		totals = sum([self.f_count(f, c) for c in self.categories()])
		bp = ((weight * average_p) + (totals * basic_prob)) / (weight + totals)
		return bp
	
	
# 朴素贝叶斯分类
class naive_bayes(classifier):
	def __init__(self, get_features):
		classifier.__init__(self, get_features)
		self.thresholds = {}
	
	def set_threshold(self, cat, t):
		self.thresholds[cat] = t
		
	def get_threshold(self, cat):
		if cat not in self.thresholds:
			return 1.0
		return self.thresholds[cat]
		
	def doc_prob(self, item, cat):
		features = self.get_features(item)
		p = 1
		for f in features:
			p *= self.weighted_prob(f, cat, self.f_prob)
		return p
	
	def prob(self, item, cat):
		cat_prob = self.c_count(cat) / self.total_count()
		doc_prob = self.doc_prob(item, cat)
		return doc_prob * cat_prob
	
	def classify(self, item, default=None):
		probs = {}
		max = 0.0
		best = default
		for cat in self.categories():
			probs[cat] = self.prob(item, cat)
			if probs[cat] > max:
				max = probs[cat]
				best = cat
		for cat in probs:
			if cat == best:
				continue
			if probs[best] < probs[cat] * self.get_threshold(best):
				return default
		return best


class fisher_classifier(classifier):
	def __init__(self, get_features):
		classifier.__init__(self, get_features)
		self.minimums = {}
	
	def set_minimum(self, cat, min):
		self.minimums[cat] = min
	
	def get_minimum(self, cat):
		if cat not in self.minimums:
			return 0
		return self.minimums[cat]
	
	def c_prob(self, f, cat):
		# 特征在该分类中出现的概率
		cl_f = self.f_prob(f, cat)
		if cl_f == 0:
			return 0
		# 特征在所有分类中出现的概率
		freq_sum = sum([self.f_prob(f, c) for c in self.categories()])
		p = cl_f / freq_sum
		return p

	def fisher_prob(self, item, cat):
		p = 1
		features = self.get_features(item)
		# 将所有概率相乘
		for f in features:
			p *= self.weighted_prob(f, cat, self.c_prob)
		# 取对数再乘-2
		f_score = -2 * math.log(p)
		# 利用倒置对数卡方函数求概率
		return self.invchi2(f_score, len(features) * 2)
	
	def invchi2(self, chi, df):
		m = chi / 2.0
		sum = term = math.exp(-m)
		for i in range(1, df // 2):
			term *= m / i
			sum += term
		return min(sum, 1.0)
	
	def classify(self, item, default=None):
		best = default
		max = 0.0
		for c in self.categories():
			p = self.fisher_prob(item, c)
			if p > self.get_minimum(c) and p > max:
				best = c
				max = p
		return best
