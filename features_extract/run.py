import news_features
import nmf
from numpy import *

all_words, article_words, article_title = news_features.get_article_words()
word_matrix, word_vec = news_features.make_matrix(all_words, article_words)
v = matrix(word_matrix)
weights, feature = nmf.factorize(v)
print(weights, feature)