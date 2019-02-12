import time
import random
import math

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]

destination = 'LGA'

flights = {}
with open('schedule.txt') as f:
	lines = f.readlines()
	for line in lines:
		origin, dest, depart, arrive, price = line.strip().split(',')
		flights.setdefault((origin, dest), [])
		
		flights[(origin, dest)].append((depart, arrive, int(price)))

def get_minutes(t):
	x = time.strptime(t, "%H:%M")
	return x[3]*60 + x[4]


def print_schedule(r):
	for d in range(int(len(r)/2)):
		name = people[d][0]
		origin = people[d][1]
		out = flights[(origin, destination)][r[2*d]]
		ret = flights[(destination, origin)][r[2*d+1]]
		print('%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin, out[0], out[1], out[2], ret[0], ret[1], ret[2]))
		

#  成本函数
def schedule_cost(sol):
	total_price = 0
	latest_arrival = 0
	earliest_dep = 24 * 60
	for d in range(int(len(sol)/2)):
		# 得到往返航班
		origin = people[d][1]
		out_bound = flights[(origin, destination)][int(sol[2*d])]
		return_flight = flights[(destination, origin)][int(sol[2*d+1])]
		
		# 计算航班价格
		total_price += out_bound[2]
		total_price += return_flight[2]
		
		# 记录最晚到达和最早离开时间
		if latest_arrival < get_minutes(out_bound[1]):
			latest_arrival = get_minutes(out_bound[1])
		if earliest_dep > get_minutes(return_flight[0]):
			earliest_dep = get_minutes(return_flight[0])
	
	# 计算所有人的等候时间，每个人在机场等到最后一个人到达为止， 并且一起在机场等候所有人都乘坐返程航班离开
	total_wait = 0
	for d in range(int(len(sol)/2)):
		origin = people[d][1]
		out_bound = flights[(origin, destination)][int(sol[2 * d])]
		return_flight = flights[(destination, origin)][int(sol[2 * d + 1])]
		total_wait += (latest_arrival - get_minutes(out_bound[1]))
		total_wait += (get_minutes(return_flight[0]) - earliest_dep)
	
	# 是否需要多付租车费用，50/天
	if latest_arrival < earliest_dep:
		total_price += 50
	return total_price+total_wait


# 随机搜索
def random_optimize(domain, cost_func):
	best = 999999999
	best_r = None
	for i in range(100000):
		r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
		cost = cost_func(r)
		if cost < best:
			# print("cost is %d" % cost)
			best = cost
			best_r = r
	# print("best cost is %d" % best)
	return best_r


# 爬山法
def hill_climb(domain, cost_func):
	# 创建随机解
	sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
	while True:
		# 创建相邻解列表
		neighbors = []
		for j in range(len(domain)):
			# 在每个方向上相对于原值偏离一点
			if sol[j] > domain[j][0]:
				neighbors.append(sol[0:j]+[sol[j]-1]+sol[j+1:])
			if sol[j] < domain[j][1]:
				neighbors.append(sol[0:j]+[sol[j]+1]+sol[j+1:])
		# 在相邻解中寻找最优解
		current = cost_func(sol)
		best = current
		for j in range(len(neighbors)):
			cost = cost_func(neighbors[j])
			if cost < best:
				# print("cost is %d" % cost)
				best = cost
				sol = neighbors[j]
		# 如果没有更优的解
		if best == current:
			break
	print("best cost is %d" % best)
	return sol
	
	
# 退火算法
def annealing_optimize(domain, cost_func, T=1000000.0, cool=0.999, step=1):
	"""
	:param domain:
	:param cost_func:
	:param T: 最大温度
	:param cool: 每次冷却比例
	:param step: 每次改变步长
	:return:
	"""
	# 随机初始化值
	vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
	while T > 0.1:
		# 随机选择一个索引值
		i = random.randint(0, len(domain)-1)
		# 随机选择一个改变索引值的方向
		dir = random.randint(-step, step)
		# 创建一个代表题解的列表， 改变其中一个值
		vecb = vec[:]
		vecb[i] += dir
		if vecb[i] < domain[i][0]:
			vecb[i] = domain[i][0]
		elif vecb[i] > domain[i][1]:
			vecb[i] = domain[i][1]
		# 计算当前成本和新成本
		ea = cost_func(vec)
		eb = cost_func(vecb)
		'''
			概率随着T的降低而降低，如果ea和eb差异变大则概率公式的计算结果会越来越小，所以该算法只倾向于接受稍差的解而不是非常差的解
			所以，如果新解更优，或者介于0到1之间的一个随机浮点数小于该公式的值，则接受新的题解
		'''
		if eb < ea or random.random() < pow(math.e, -(eb-ea)/T):
			vec = vecb
		# 降低温度
		T *= cool
	print("best cost is %d" % ea)
	return vec


# 遗传算法
def genetic_optimize(domain, cost_func, pop_size=50, step=1, mut_prob=0.2, elite=0.2, max_iter=100):
	"""
	:param domain: 
	:param cost_func: 
	:param pop_size: 种群大小
	:param step: 
	:param mut_prob: 种群新成员是由变异而非交叉得来的概率 
	:param elite: 种群中允许传入下一代的部分
	:param max_iter: 最大迭代次数
	:return: 
	"""
	# 变异操作
	def mutate(vec):
		i = random.randint(0, len(domain)-1)
		if random.random() < 0.5 and vec[i] > domain[i][0]:
			return vec[0:i]+[vec[i]-step]+vec[i+1:]
		elif vec[i] < domain[i][1]:
			return vec[0:i]+[vec[i]+step]+vec[i+1:]
		
	# 交叉操作
	def crossover(r1, r2):
		r = random.randint(0, len(domain)-2)
		return r1[0:r]+r2[r:]
	# 构造初始种群
	pop = []
	for i in range(pop_size):
		vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
		pop.append(vec)
	# 每一代中的精英数量
	top_elite = int(elite*pop_size)
	# 主循环
	scores = []
	for j in range(max_iter):
		scores = [(cost_func(v), v) for v in pop if v is not None]
		scores.sort()
		ranked = [v for s, v in scores]
		# 从最优精英开始
		pop = ranked[0:top_elite]
		# 添加变异和配对后的最优精英
		while len(pop) < pop_size:
			if random.random() < mut_prob:
				# 变异
				c = random.randint(0, top_elite-1)
				pop.append(mutate(ranked[c]))
			else:
				# 交叉
				c1 = random.randint(0, top_elite-1)
				c2 = random.randint(0, top_elite-1)
				pop.append(crossover(ranked[c1], ranked[c2]))
		# 打印当前最优值
		print(scores[0][0])	
	return scores[0][1]
		
				

