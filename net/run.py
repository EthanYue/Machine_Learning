import nn
my_net = nn.searching_net()
# my_net.db_setup()
wWorld, wRiver, wBank = 101, 102, 103
uWorldBank, uRiver, uEarth = 201, 202, 203
all_urls = [uWorldBank, uRiver, uEarth]
# my_net.generate_hidden_node([wWorld, wBank], [uWorldBank, uRiver, uEarth])
# for i in range(30):
# 	my_net.train_query([wWorld, wBank], all_urls, uWorldBank)
# 	my_net.train_query([wRiver, wBank], all_urls, uRiver)
# 	my_net.train_query([wWorld], all_urls, uEarth)
# res1 = my_net.get_result([wWorld, wBank], all_urls)
# res2 = my_net.get_result([wRiver, wBank], all_urls)
res3 = my_net.get_result([uRiver], all_urls)
print(res3)
