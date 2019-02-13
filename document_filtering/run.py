import doc_class

_class = doc_class.classifier(doc_class.get_words)
doc_class.sample_train(_class)
res = _class.f_prob('quick', 'good')
print(res)