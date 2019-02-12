import math
from PIL import Image, ImageDraw

people = ['Charlie', 'Augustus', 'Veruca', 'Violet', 'Mike', 'Joe', 'Willy', 'Miranda']
domain = [(10, 370)] * (len(people) * 2)
links = [('Augustus', 'Willy'),
         ('Mike', 'Joe'),
         ('Miranda', 'Mike'),
         ('Violet', 'Augustus'),
         ('Miranda', 'Willy'),
         ('Charlie', 'Mike'),
         ('Veruca', 'Joe'),
         ('Miranda', 'Augustus'),
         ('Willy', 'Augustus'),
         ('Joe', 'Charlie'),
         ('Veruca', 'Augustus'),
         ('Miranda', 'Joe')]


def cross_count(v):
	# 将数字序列转换为person:(x,y)的字典
	loc = dict([(people[i], (v[i * 2], v[i * 2 + 1])) for i in range(0, len(people))])
	total = 0
	# 遍历所有连线
	for i in range(len(links)):
		for j in range(i + 1, len(links)):
			# 获取坐标位置
			(x1, y1), (x2, y2) = loc[links[i][0]], loc[links[i][1]]
			(x3, y3), (x4, y4) = loc[links[j][0]], loc[links[j][1]]
			den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
			# 是否平行
			if den == 0:
				continue
			# ua， ub为两条连线的分数值， 如果该值介于0，1之间，则两线交叉
			ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
			ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
			if ua > 0 and ua < 1 and ub > 0 and ub < 1:
				total += 1
	return total


def draw_network(sol):
	# 建立Image对象
	img = Image.new('RGB', (400, 400), (255, 255, 255))
	draw = ImageDraw.Draw(img)
	# 将数字序列转换为person:(x,y)的字典
	pos = dict([(people[i], (sol[i * 2], sol[i * 2 + 1])) for i in range(0, len(people))])
	# 绘制连线
	for name_a, name_b in links:
		draw.line(pos[name_a], pos[name_b], fill='black')
	# 绘制人名
	for name, _pos in pos.items():
		draw.text(_pos, name, (0, 0, 0))
	img.show()
