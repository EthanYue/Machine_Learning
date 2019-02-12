from math import tanh
import pymysql


def dtanh(y):
	return 1.0-y*y


class searching_net:
	def __init__(self):
		self.db = pymysql.connect("127.0.0.1", "root", "yuefeiyu", "nn")
		self.cur = self.db.cursor()
	
	def __del__(self):
		self.db.close()
		
	def db_setup(self):
		self.cur.execute('drop table if exists hidden_node')
		self.cur.execute('drop table if exists word_hidden')
		self.cur.execute('drop table if exists hidden_url')
		self.cur.execute('create table hidden_node (rowid int not null primary key auto_increment, create_key varchar(512))')
		self.cur.execute('create table word_hidden (rowid int not null primary key auto_increment, from_id int, to_id int, strength float)')
		self.cur.execute('create table hidden_url (rowid int not null primary key auto_increment, from_id int, to_id int, strength float)')
		try:
			self.db.commit()
		except Exception as e:
			print(e)
			print('create tables failed')
	
	def get_strength(self, from_id, to_id, layer):
			table = 'word_hidden' if layer == 0 else 'hidden_url'
			self.cur.execute('select strength from %s where from_id=%d and to_id=%d' % (table, from_id, to_id))
			res = self.cur.fetchone()
			if res is None:
				if layer == 0:
					return -0.2
				if layer == 1:
					return 0
			return res[0]
	
	def set_strength(self, from_id, to_id, layer, strength):
		table = 'word_hidden' if layer == 0 else 'hidden_url'
		self.cur.execute('select rowid from %s where from_id=%d and to_id=%d' % (table, from_id, to_id))
		res = self.cur.fetchone()
		if res is None:
			self.cur.execute('insert into %s (from_id, to_id, strength) values (%d, %d, %f)' % (table, from_id, to_id, strength))
		else:
			rowid = res[0]
			self.cur.execute('update %s set strength=%f where rowid=%d' % (table, strength, rowid))
			
	def generate_hidden_node(self, word_ids, urls):
		if len(word_ids) > 3:
			return None
		create_key = '_'.join(sorted([str(wi) for wi in word_ids]))
		self.cur.execute("select rowid from hidden_node where create_key='%s'" % create_key)
		res = self.cur.fetchone()
		if res is None:
			self.cur.execute("insert into hidden_node (create_key) values ('%s')" % create_key)
			hidden_id = self.cur.lastrowid
			for word_id in word_ids:
				self.set_strength(word_id, hidden_id, 0, 1.0/len(word_ids))
			for url_id in urls:
				self.set_strength(hidden_id, url_id, 1, 0.1)
			try:
				self.db.commit()
			except Exception as e:
				print(e)
				print('generate_hidden_nodes failed')

	def get_all_hidden_ids(self, word_ids, url_ids):
		l1 = {}
		for word_id in word_ids:
			self.cur.execute('select to_id from word_hidden where from_id=%d' % word_id)
			for row in self.cur.fetchall():
				l1[row[0]] = 1
		for url_id in url_ids:
			self.cur.execute('select from_id from hidden_url where to_id=%d' % url_id)
			for row in self.cur.fetchall():
				l1[row[0]] = 1
		return list(l1.keys())
	
	# 建立网络
	def setup_network(self, word_ids, url_ids):
		# 值列表
		self.word_ids = word_ids
		self.hidden_ids = self.get_all_hidden_ids(word_ids, url_ids)
		self.url_ids = url_ids
		
		# 节点输出
		self.ai = [1.0] * len(self.word_ids)
		self.ah = [1.0] * len(self.hidden_ids)
		self.ao = [1.0] * len(self.url_ids)
		
		# 建立权重矩阵
		self.wi = [[self.get_strength(word_id, hidden_id, 0) for hidden_id in self.hidden_ids] for word_id in self.word_ids]
		self.wo = [[self.get_strength(hidden_id, url_id, 1) for url_id in self.url_ids] for hidden_id in self.hidden_ids]
		
	def feed_forward(self):
		# 查询单词是仅有的输入
		for i in range(len(self.word_ids)):
			self.ai[i] = 1.0
			
		# 隐藏层节点的活跃程度
		for j in range(len(self.hidden_ids)):
			sum = 0.0
			for i in range(len(self.word_ids)):
				sum += self.ai[i] * self.wi[i][j]
			self.ah[j] = tanh(sum)
				
		# 输出层节点的活跃程度
		for k in range(len(self.url_ids)):
			sum = 0.0
			for j in range(len(self.hidden_ids)):
				sum += self.ah[j] * self.wo[j][k]
			self.ao[k] = tanh(sum)
		return self.ao[:]
		
	def get_result(self, word_ids, url_ids):
		self.setup_network(word_ids, url_ids)
		return self.feed_forward()

	def back_Propagate(self, targets, N=0.5):
		# 计算输出层的误差
		output_deltas = [0.0] * len(self.url_ids)
		for k in range(len(self.url_ids)):
			error = targets[k] - self.ao[k]
			output_deltas[k] = dtanh(self.ao[k]) * error
		
		# 计算隐藏层的误差
		hidden_deltas = [0.0] * len(self.hidden_ids)
		for j in range(len(self.hidden_ids)):
			error = 0.0
			for k in range(len(self.url_ids)):
				error += output_deltas[k] * self.wo[j][k]
			hidden_deltas[j] = dtanh(self.ah[j]) * error
		
		# 更新输出权重
		for j in range(len(self.hidden_ids)):
			for k in range(len(self.url_ids)):
				change = output_deltas[k] * self.ah[j]
				self.wo[j][k] += N*change
		
		# 更新输入权重
		for i in range(len(self.word_ids)):
			for j in range(len(self.hidden_ids)):
				change = hidden_deltas[j] * self.ai[i]
				self.wi[i][j] += N*change

	def train_query(self, word_ids, url_ids, selected_url):
		self.generate_hidden_node(word_ids, url_ids)
		self.setup_network(word_ids, url_ids)
		self.feed_forward()
		targets = [0.0] * len(url_ids)
		targets[url_ids.index(selected_url)] = 1.0
		self.back_Propagate(targets)
		self.update_database()
		
	def update_database(self):
		for i in range(len(self.word_ids)):
			for j in range(len(self.hidden_ids)):
				self.set_strength(self.word_ids[i], self.hidden_ids[j], 0, self.wi[i][j])
		for j in range(len(self.hidden_ids)):
			for k in range(len(self.url_ids)):
				self.set_strength(self.hidden_ids[j], self.url_ids[k], 1, self.wo[j][k])
		try:
			self.db.commit()
		except Exception as e:
			print(e)
