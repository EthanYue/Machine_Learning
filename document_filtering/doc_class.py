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
		return self.f_count(f, cat)/self.c_count(cat)
