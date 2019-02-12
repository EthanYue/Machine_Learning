import random
import math

dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']

prefs = [('Toby', ('Bacchus', 'Hercules')),
         ('Steve', ('Zeus', 'Pluto')),
         ('Andrea', ('Athena', 'Zeus')),
         ('Sarah', ('Zeus', 'Pluto')),
         ('Dave', ('Athena', 'Bacchus')),
         ('Jeff', ('Hercules', 'Pluto')),
         ('Fred', ('Pluto', 'Athena')),
         ('Suzie', ('Bacchus', 'Hercules')),
         ('Laura', ('Bacchus', 'Hercules')),
         ('Neil', ('Hercules', 'Athena'))]

domain = [(0, (len(dorms) * 2) - i - 1) for i in range(0, len(dorms) * 2)]


def print_sol(vec):
	slots = []
	# 为每个宿舍建两个槽
	for i in range(len(dorms)):
		slots += [i, i]
	# 遍历安置情况
	for i in range(len(vec)):
		x = int(vec[i])
		# 从剩余槽中选择
		dorm = dorms[slots[x]]
		# 输出学生及被分配的宿舍
		print(prefs[i][0], dorm)
		# 删除该槽
		del slots[x]


def dorm_cost(vec):
	cost = 0
	slots = []
	for i in range(len(dorms)):
		slots += [i, i]
	for i in range(len(vec)):
		x = int(vec[i])
		dorm = dorms[slots[x]]
		# 获得每个学生的宿舍偏好
		pref = prefs[i][1]
		# 为首选则成本+0， 为次选则成本+1， 为其他则成本+3
		if pref[0] == dorm:
			cost += 0
		elif pref[1] == dorm:
			cost += 1
		else:
			cost +=3
		del slots[x]
	return cost
	