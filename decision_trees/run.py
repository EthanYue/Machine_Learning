import tree_predict
set1, set2 = tree_predict.divide_set(tree_predict.my_data, 2, 'yes')
# res = tree_predict.gini_impurity(tree_predict.my_data)
# res = tree_predict.entropy(tree_predict.my_data)
# res = tree_predict.entropy(set1)
tree = tree_predict.build_tree(tree_predict.my_data)
tree_predict.draw_tree(tree)