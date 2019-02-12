import re
import urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pymysql
from net import nn
# from sqlite3 import dbapi2 as sqlite

my_net = nn.searching_net()
ignore_words = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


class crawler:
	def __init__(self):
		self.db = pymysql.connect("127.0.0.1", "root", "yuefeiyu", "search_index")
		self.cur = self.db.cursor()
	
	def __del__(self):
		self.db.close()
	
	def db_drop_one(self, table_name):
		self.cur.execute('delete from %s' % table_name)
		try:
			self.db.commit()
		except Exception as e:
			print(e)
			print('delete table failed')
	
	def db_drop_all(self):
		self.cur.execute("show tables")
		_tables = self.cur.fetchall()
		for _table in _tables:
			self.cur.execute('delete from %s' % _table[0])
		try:
			self.db.commit()
			print('delete table success')
		except Exception as e:
			print(e)
			print('delete table failed')

	def db_commit(self):
		self.db.commit()
	
	def get_entryid(self, table, field, value, createnew=True):
		self.cur.execute("select rowid from %s where %s='%s'" % (table, field, value))
		cur = self.cur.fetchone()
		if cur is None:
			self.cur.execute("insert into %s (%s) values ('%s')" % (table, field, value))
			return self.con.lastrowid
		else:
			return cur[0]
	
	def add_index(self, url, soup):
		if self.is_indexed(url):
			return
		print('Indexing %s' % url)
		
		# 获取每个单词
		text = self.get_textonly(soup)
		words = self.separate_words(text)
		
		# 得到url的id
		url_id = self.get_entryid('url_list', 'url', url)
		
		# 将每个单词与该url关联
		_tmp = {}
		for i in range(len(words)):
			word = words[i]
			if word in ignore_words:
				continue
			word_id = self.get_entryid('word_list', 'word', word)
			if not _tmp.get("%d %d" % (url_id, word_id)):
				_tmp.setdefault("%d %d" % (url_id, word_id), [])
			_tmp["%d %d" % (url_id, word_id)].append(str(i))
		for j in _tmp:
			url_id = int(j.split()[0])
			word_id = int(j.split()[1])
			_location = ','.join(_tmp[j])
			self.cur.execute("insert into word_location(url_id, word_id, location) values (%d,%d,'%s')" % (url_id, word_id, _location))
			self.cur.execute("insert into link_words (link_id, word_id) values (%d, %d)" % (url_id, word_id))
		try:
			self.db.commit()
		except Exception as e:
			print(e)
	
	def get_textonly(self, soup):
		v = soup.string
		if v is None:
			c = soup.contents
			result_text = ''
			for t in c:
				subtext = self.get_textonly(t)
				result_text += subtext + '\n'
			return result_text
		else:
			return v.strip()
	
	def separate_words(self, text):
		splitter = re.compile(r'\W')
		return [s.lower() for s in splitter.split(text) if s != '']
	
	def is_indexed(self, url):
		self.cur.execute("select rowid from url_list where url='%s'" % url)
		_res = self.cur.fetchone()
		if _res is not None:
			self.cur.execute('select * from word_location where url_id=%d' % _res)
			v = self.cur.fetchone()
			if v is not None:
				return True
		return False
	
	def add_link_ref(self, from_id, to_id, link_text):
		from_id = self.get_entryid('url_list', 'url', from_id)
		to_id = self.get_entryid('url_list', 'url', to_id)
		sql = "insert into link (from_id, to_id, link_text) values (%s, %s, %s)"
		try:
			self.cur.execute(sql, (from_id, to_id, link_text))
			self.db.commit()
		except Exception as e:
			print(e)
			print('insert link table failed, %s' % sql)
			
	def db_setup(self):
		self.cur.execute('drop table if exists url_list')
		self.cur.execute('drop table if exists word_list')
		self.cur.execute('drop table if exists word_location')
		self.cur.execute('drop table if exists link')
		self.cur.execute('drop table if exists link_words')
		
		self.cur.execute('create table url_list(rowid int not null primary key auto_increment, url varchar(512))')
		self.cur.execute('create table word_list(rowid int not null primary key auto_increment, word varchar(512))')
		self.cur.execute('create table word_location(rowid int not null primary key auto_increment, url_id int, word_id int, location text)')
		self.cur.execute('create table link(rowid int not null primary key auto_increment, from_id int, to_id int, link_text text)')
		self.cur.execute('create table link_words(rowid int not null primary key auto_increment, word_id int, link_id int)')
		self.cur.execute('create index word_idx on word_list(word)')
		self.cur.execute('create index url_idx on url_list(url)')
		self.cur.execute('create index word_url_idx on word_location(word_id)')
		self.cur.execute('create index url_to_idx on link(to_id)')
		self.cur.execute('create index url_from_idx on link(from_id)')
		try:
			self.db.commit()
			print('create tables success')
		except Exception as e:
			print(e)
			print('create tables failed')
	
	def db_update(self, tables):
		if isinstance(tables, dict):
			for table in tables:
				self.cur.execute('drop table if exists %s' % table)
				self.cur.execute('create table %s(%s)' % (table, tables.get(table)))
		try:
			self.db.commit()
			print('update table success')
		except Exception as e:
			print(e)
			print('update table failed')

	
	def crawl(self, pages, depth=2):
		for i in range(depth):
			new_pages = set()
			for page in pages:
				try:
					c = urllib.request.urlopen(page)
				except:
					print('Could not open %s' % page)
					continue
				soup = BeautifulSoup(c.read(), features="html.parser")
				self.add_index(page, soup)
				
				links = soup('a')
				for link in links:
					if 'href' in dict(link.attrs):
						url = urljoin(page, link['href'])
						if url.find("'") != -1:
							continue
						url = url.split('#')[0]
						if url[0:4] == 'http' and not self.is_indexed(url):
							new_pages.add(url)
						linkText = self.get_textonly(link)
						self.add_link_ref(page, url, linkText)
			pages = new_pages
	
	def cal_page_rank(self, iterations=20):
		self.cur.execute('drop table if exists page_rank')
		self.cur.execute('create table page_rank (url_id int primary key, score float)')
		
		self.cur.execute('insert into page_rank select rowid, 1.0 from url_list')
		try:
			self.db.commit()
		except Exception as e:
			print(e)
		
		for i in range(iterations):
			print('Iteration %s' % i)
			self.cur.execute('select rowid from url_list')
			for (url_id, ) in self.cur.fetchall():
				pr = 0.15
				self.cur.execute('select distinct from_id from link where to_id=%d' % url_id)
				for (linker, ) in self.cur.fetchall():
					self.cur.execute('select score from page_rank where url_id=%d' % linker)
					linking_pr = self.cur.fetchone()[0]
					self.cur.execute('select count(*) from link where from_id=%d' % linker)
					linking_count = self.cur.fetchone()[0]
					pr += 0.85 * (linking_pr / linking_count)
				self.cur.execute('update page_rank set score=%f where url_id=%d' % (pr, url_id))
			try:
				self.db.commit()
			except Exception as e:
				print(e)



class searcher:
	def __init__(self, db_name):
		self.db = pymysql.connect("127.0.0.1", "root", "yuefeiyu", "search_index")
		self.cur = self.db.cursor()
		
	def __del__(self):
		self.db.close()
	
	def get_match_rows(self, q):
		# 构造查询的字符串
		field_list = 'w0.url_id'
		table_list = ''
		clause_list = ''
		word_ids = []
		
		# 根据空格拆分单词
		words = q.split(',')
		table_number = 0
		for word in words:
			# 获取单词id
			self.cur.execute("select rowid from word_list where word='%s'" % word)
			word_row = self.cur.fetchone()
			if word_row is None:
				return False, 'no word'
			word_id = word_row[0]
			word_ids.append(word_id)
			if table_number > 0:
				table_list += ','
				clause_list += ' and '
				clause_list += 'w%d.url_id=w%d.url_id and ' % (table_number-1, table_number)
			field_list += ',w%d.location' % table_number
			table_list += 'word_location w%d' % table_number
			clause_list += 'w%d.word_id=%d' % (table_number, word_id)
			table_number += 1
		
		# 建立查询
		full_query = 'select %s from %s where %s' % (field_list, table_list, clause_list)
		self.cur.execute(full_query)
		cur = self.cur.fetchall()
		rows = [row for row in cur]
		return rows, word_ids
	
	def get_scored_list(self, rows, word_ids):
		total_scores = dict([(row[0], 0) for row in rows])
		# weights = [(1.0, self.location_score(rows)), (1.0, self.frequency_score(rows)), (1.0, self.page_rank_score(rows))]
		# weights = [(1.0, self.distance_score(rows))]
		# weights = [(1.0, self.page_rank_score(rows))]
		# weights = [(1.0, self.link_text_score(rows, word_ids))]
		weights = [(1.0, self.net_score(rows, word_ids))]
		for weight, scores in weights:
			for url in total_scores:
				total_scores[url] += weight * scores.get(url, 0.00001)
		return total_scores
	
	def get_url_name(self, id):
		self.cur.execute("select url from url_list where rowid=%d" % id)
		return self.cur.fetchone()[0]
	
	def query(self, q):
		rows, word_ids = self.get_match_rows(q)
		if not rows:
			return False
		scores = self.get_scored_list(rows, word_ids)
		ranked_scores = sorted([(score, url) for (url, score) in scores.items()], reverse=True)
		for (score, url_id) in ranked_scores[0:15]:
			print('%f\t%s' % (score, self.get_url_name(url_id)))
		return word_ids, [r[1] for r in ranked_scores[0:10]]
	
	def normalization_scores(self, scores, small_is_better=True):
		v_small = 0.00001
		if small_is_better:
			min_score = min([score for score in scores.values() if score > 0])
			return dict([(u, float(min_score) / max(v_small, l)) for (u, l) in scores.items()])
		else:
			max_score = max(scores.values())
			if max_score == 0:
				max_score = v_small
			return dict([(u, float(c) / max_score) for (u, c) in scores.items()])
	
	def frequency_score(self, rows):
		counts = dict([(row[0], 0) for row in rows])
		for row in rows:
			counts[row[0]] += len(row[1])
		return self.normalization_scores(counts)
	
	def location_score(self, rows):
		locations = dict([(row[0], 1000000) for row in rows])
		for row in rows:
			loc = sum([int(i) for i in row[1].split(',')])
			if loc < locations[row[0]]:
				locations[row[0]] = loc
		return self.normalization_scores(locations, small_is_better=True)

	def distance_score(self, rows):
		min_distance = dict([(row[0], 1000000) for row in rows])
		for row in rows:
			_loc = [int(i) for i in row[1].split(',')]
			if len(_loc) <= 1:
				min_distance[row[0]] = 1.0
				continue
			dist = sum([abs(_loc[i]-_loc[i-1]) for i in range(1, len(_loc))])
			if dist < min_distance[row[0]]:
				min_distance[row[0]] = dist
		return self.normalization_scores(min_distance, small_is_better=True)

	def page_rank_score(self, rows):
		_ranks = []
		for row in rows:
			self.cur.execute('select score from page_rank where url_id=%d' % row[0])
			_ranks.append((row[0], self.cur.fetchone()[0]))
		page_ranks = dict(_ranks)
		max_rank = max(page_ranks.values())
		nomalization_scores = dict([(u, float(l)/max_rank) for (u, l) in page_ranks.items()])
		return nomalization_scores
	
	def link_text_score(self, rows, word_ids):
		link_scores = dict([(row[0], 0) for row in rows])
		for word_id in word_ids:
			self.cur.execute('select link.from_id, link.to_id from link_words, link where word_id=%d and link_words.link_id=link.from_id' % word_id)
			cur = self.cur.fetchall()
			for (from_id, to_id) in cur:
				if to_id in link_scores:
					self.cur.execute('select score from page_rank where url_id=%d' % from_id)
					pr = self.cur.fetchone()[0]
					link_scores[to_id] += pr
		max_score = max(link_scores.values())
		nomalization_scores = dict([(u, float(l)/max_score) for (u, l) in link_scores.items()])
		return nomalization_scores
	
	def net_score(self, rows, word_ids):
		url_ids = [url_id for url_id in set([row[0] for row in rows])]
		my_net.generate_hidden_node(word_ids, url_ids)
		net_res = my_net.get_result(word_ids, url_ids)
		scores = dict([(url_ids[i], net_res[i]) for i in range(len(url_ids))])
		return self.normalization_scores(scores)
