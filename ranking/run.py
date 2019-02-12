import search_engine
# pagelist = ['http://kiwitobes.com/wiki/Prel.html']
# pagelist = ['https://pypi.org/search']
# crawler = search_engine.crawler()
# crawler.db_drop_all()
# crawler.db_setup()
# crawler.db_update({'link': 'from_id, to_id, link_text'})
# crawler.crawl(pagelist)
# print('crawler down')
# crawler.cal_page_rank()
engine = search_engine.searcher('search_index.db')
# res = engine.get_match_rows('pip')
res = engine.query('python')
print(res)

