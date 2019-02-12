import feedparser
import re


def getwordcounts(url):
	d = feedparser.parse(url)
	wc = {}
	for e in d.entries:
		if 'summary' in e:
			summary = e.summary
		else:
			summary = e.description
		words = getwords(e.title + '' + summary)
		for word in words:
			wc.setdefault(word, 0)
			wc[word] += 1
	return d.feed.link, wc


def getwords(html):
	# 去除所有html标签
	txt = re.compile(r'<[^>]+>').sub('', html)
	# 用非字母字符拆分出单词
	words = re.compile(r'[^A-Z^a-z]').split(txt)
	return [word.lower() for word in words if word != '']


apcount = {}
wordcounts = {}
with open('feedlist.txt') as f:
	lines = f.readlines()
feedlist = [line for line in lines]
for feedurl in feedlist:
	title, wc = getwordcounts(feedurl)
	wordcounts[title] = wc
	for word, count in wc.items():
		apcount.setdefault(word, 0)
		if count > 1:
			apcount[word] += 1
wordlist = []
for w, bc in apcount.items():
	frac = float(bc) / len(feedlist)
	if frac > 0.1 and frac < 0.5:
		wordlist.append(w)
		
with open('blogdata.txt', 'a+') as f:
	f.write('Blog')
	for word in wordlist:
		f.write('\t%s' % word)
	f.write('\n')
	for blog, wc in wordcounts.items():
		f.write(blog)
		for word in wordlist:
			if word in wc:
				f.write('\t%d' % wc[word])
			else:
				f.write('\t0')
		f.write('\n')
