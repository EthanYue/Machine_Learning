import feedparser
import re

feed_list = ['https://www.foxnews.com/xmlfeed/rss/0,4313,0,00.rss',
             'https://www.foxnews.com/xmlfeed/rss/0,4313,80,00.rss',
             'https://www.foxnews.com/xmlfeed/rss/0,4313,81,00.rss',
             'http://rss.cnn.com/rss/edition.rss',
             'http://rss.cnn.com/rss/edition_us.rss',
             'http://blog.csdn.net/together_cz',
             'https://blog.csdn.net/boling_cavalry',
             'https://blog.csdn.net/kangshaojun888',
             'https://blog.csdn.net/qing_gee',
             'https://blog.csdn.net/weixin_44239541',
             'https://blog.csdn.net/florachy',
             'https://blog.csdn.net/a4171175',
             'https://blog.csdn.net/mo3408']


def stripHTML(h):
	p = ''
	s = 0
	for c in h:
		if c == '<':
			s = 1
		elif c == '>':
			s = 0
			p += ''
		elif s == 0:
			p += c
	return p


def separate_words(text):
	splitter = re.compile(r'\W')
	return [s.lower() for s in splitter.split(text) if len(s) > 3]


def get_article_words():
	all_words = {}
	article_words = []
	article_titles = []
	ec = 0
	# 遍历订阅源
	for feed in feed_list:
		f = feedparser.parse(feed)
		# 遍历每篇文章
		for e in f.entries:
			if e.title in article_titles:
				continue
			# 提取单词
			txt = e.title + stripHTML(e.description.encode('utf8'))
			words = separate_words(txt)
			article_words.append({})
			article_titles.append(e.title)
			# 增加计数
			for word in words:
				all_words.setdefault(word, 0)
				all_words[word] += 1
				article_words[ec].setdefault(word, 0)
				article_words[ec][word] += 1
			ec += 1
	return all_words, article_words, article_titles


def make_matrix(all_words, article_words):
	word_vec = []
	for w, c in all_words.items():
		if 1 < c < len(article_words) * 0.9:
			word_vec.append(w)
	l1 = [[(word in f and f[word] or 0) for word in word_vec] for f in article_words]
	return l1, word_vec

