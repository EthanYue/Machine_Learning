from random import random, randint, choice
from copy import deepcopy
from math import log


class fw_rapper:
	def __init__(self, function, child_count, name):
		self.function = function
		self.child_count = child_count
		self.name = name
		

class node:
	def __init__(self, fw, children):
		self.function = fw.function
		self.name = fw.name
		self.children = children
		
	def evaluate(self, inp):
		results = [n.evaluate(inp) for n in self.children]
		return self.function(results)
	
	def display(self, indent=0):
		print('     ' * indent + self.name)
		for c in self.children:
			c.display(indent+1)
		
	

class param_node:
	def __init__(self, idx):
		self.idx = idx
		
	def evaluate(self, inp):
		return inp[self.idx]
	
	def display(self, indent=0):
		print('%sp%d' % ('      ' * indent, self.idx))
	

class const_node:
	def __init__(self, v):
		self.v = v
	
	def evaluate(self, inp):
		return self.v
	
	def display(self, indent=0):
		print('%s%d' % ('       ' * indent, self.v))

	
add_w = fw_rapper(lambda l: l[0] + l[1], 2, 'add')
sub_w = fw_rapper(lambda l: l[0] - l[1], 2, 'subtract')
mul_w = fw_rapper(lambda l: l[0] * l[1], 2, 'multiply')


def if_func(l):
	return l[1] if l[0] > 0 else l[2]


if_w = fw_rapper(if_func, 3, 'if')


def is_greater(l):
	return 1 if l[0] > l[1] else 0


gt_w = fw_rapper(is_greater, 2, 'is_greater')

f_list = [add_w, mul_w, if_w, gt_w, sub_w]


def example_tree():
	return node(if_w, [node(gt_w, [param_node(0), const_node(3)]), node(add_w, [param_node(1), const_node(5)]), node(sub_w, [param_node(1), const_node(2)]),])


# 随机生成函数
def make_random_tree(pc, max_depth=4, fpr=0.5, ppr=0.6):
	"""
	:param pc: param_count
	:param max_depth:
	:param fpr: function_prob 新建节点属于函数型节点的概率
	:param ppr: param_prob 新建节点不是函数型节点时，属于param_node的概率
	:return:
	"""
	if random() < fpr and max_depth > 0:
		f = choice(f_list)
		children = [make_random_tree(pc, max_depth-1, fpr, ppr) for i in range(f.child_count)]
		return node(f, children)
	elif random() < ppr:
		return param_node(randint(0, pc-1))
	else:
		return const_node(randint(0, 10))


def hidden_function(x, y):
	return x ** 2 + 2 * y + 3 * x + 5


# 构建数据集
def build_hidden_set():
	rows = []
	for i in range(200):
		x = randint(0, 40)
		y = randint(0, 40)
		rows.append([x, y, hidden_function(x, y)])
	return rows


# 衡量题解优劣程度
def score_function(tree, s):
	dif = 0
	for data in s:
		v = tree.evaluate([data[0], data[1]])
		dif += abs(v - data[2])
	return dif


# 对随机生成的函数进行变异，从根节点逐一判断子节点是否应该变异
def mutate(t, pc, prob_change=0.2):
	if random() < prob_change:
		return make_random_tree(pc)
	else:
		result = deepcopy(t)
		if isinstance(t, node):
			result.children = [mutate(c, pc, prob_change) for c in t.children]
		return result


def crossover(t1, t2, prob_swap=0.7, top=1):
	if random() < prob_swap and not top:
		return deepcopy(t2)
	else:
		result = deepcopy(t1)
		if isinstance(t1, node) and isinstance(t2, node):
			result.children = [crossover(c, choice(t2.children), prob_swap, 0) for c in t1.children]
		return result


def evolve(pc, pop_size, rank_function, max_gen=50, mutation_rate=0.1, breeding_rate=0.4, p_exp=0.7, p_new=0.1):
	"""
	:param pc: param_count
	:param pop_size: 种群数量 
	:param rank_function: 对不同成员进行评分并排序的函数
	:param max_gen: 最大迭代数
	:param mutation_rate: 变异率
	:param breeding_rate: 交叉率
	:param p_exp: 过滤种群的严格程度，值越小越严格
	:param p_new: 在下一代中引入新成员的概率
	:return: 
	"""
	def select_index():
		return int(log(random())/log(p_exp))
	# 随机构造种群
	population = [make_random_tree(pc) for i in range(pop_size)]
	for i in range(max_gen):
		scores = rank_function(population)
		print(scores[0][0])
		# 如果找到最优解则退出
		if scores[0][0] == 0:
			break
		# 精英选拔
		new_pop = [scores[0][1], scores[1][1]]
		while len(new_pop) < pop_size:
			# 如果满足引入新成员的概率则随机创建新成员，否则进行交叉变异
			if random() > p_new:
				new_pop.append(mutate(crossover(scores[select_index()][1], scores[select_index()][1], prob_swap=breeding_rate), pc, prob_change=mutation_rate))
			else:
				new_pop.append(make_random_tree(pc))
		population = new_pop
	scores[0][1].display()
	return scores[0][1]


def get_rank_function(data_set):
	def rank_function(population):
		scores = [(score_function(t, data_set), t) for t in population]
		res = sorted(scores, key=lambda x: x[0])
		return res
	return rank_function


def grid_game(p):
	# 游戏区域
	max = (3, 3)
	# 记录玩家的上一步
	last_move = [-1, -1]
	# 记录玩家的位置
	location = [[randint(0, max[0]), randint(0, max[1])]]
	location.append([(location[0][0] + 2) % 4, (location[0][1] + 2) % 4])
	# 最大移动步数
	for s in range(50):
		# 每位玩家
		for i in range(2):
			locs = location[i][:] + location[1-i][:]
			locs.append(last_move[i])
			move = p[i].evaluate(locs) % 4
			# 如果两次移动相同，则判负
			if last_move[i] == move:
				# 返回获胜玩家
				return 1-i
			last_move[i] = move
			if move == 0:
				location[i][0] -= 1
				# 限制游戏区域
				if location[i][0] < 0:
					location[i][0] = 0
			if move == 1:
				location[i][0] += 1
				if location[i][0] > max[0]:
					location[i][0] = max[0]
			if move == 2:
				location[i][1] += 1
				if location[i][0] > max[1]:
					location[i][1] = max[1]
			# 如果双方走到同意位置，则分出胜负
			if location[i] == location[1-i]:
				return i
	return -1


def tournament(p1):
	# 统计失败次数
	losses = [0 for p in p1]
	# 玩家一一对抗
	for i in range(len(p1)):
		for j in range(len(p1)):
			if i == j:
				continue
			winner = grid_game([p1[i], p1[j]])
			if winner == 0:
				losses[j] += 2
			elif winner == 1:
				losses[i] += 2
			elif winner == -1:
				losses[i] += 1
				losses[j] += 1
				pass
	z = zip(losses, p1)
	res = sorted(z, key=lambda x: x[0])
	return res
	

# class human_player:
# 	def evaluate(self, board):
# 		me = tuple(board[0:2])
# 		others = [tuple(board[x:x+2]) for x in range(2, len(board)-1, 2)]
# 		for i in range(4):
# 			for j in range(4):
# 				if (i, j) == me:
# 					print('O ', end='')
# 				elif (i, j) in others:
# 					print('X ', end='')
# 				else:
# 					print('. ', end='')
# 			print()
# 		print('Your last move was %d' % board[len(board)-1])
# 		print(' 0')
# 		print('2 3')
# 		print(' 1')
# 		print('Enter your move: ')
# 		move = int(input())
# 		return move