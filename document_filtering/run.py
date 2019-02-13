import doc_class
# import naive_bayes


# naive_bayes = doc_class.naive_bayes(doc_class.get_words)
fisher_classifier = doc_class.fisher_classifier(doc_class.get_words)
fisher_classifier.set_db()
doc_class.sample_train(fisher_classifier)
# res = naive_bayes.classify('quick rabbit', 'unknown')
# naive_bayes.set_threshold('bad', 3.0)
# res = fisher_classifier.weighted_prob('quick money', 'good', fisher_classifier.c_prob)
# res = fisher_classifier.fisher_prob('quick rabbit', 'bad')
fisher_classifier.set_minimum('bad', 0.8)
# fisher_classifier.set_minimum('good', 0.4)
res = fisher_classifier.classify('quick money')
print(res)
