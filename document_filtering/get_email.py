import poplib
from email.parser import Parser
import base64


def decode_base64(s, charset='utf8'):
	return str(base64.decodebytes(s.encode(encoding=charset)), encoding=charset)


def get_parsed_msg():
	user_account = 'ethanyue007@163.com'
	password = '98333498yfy'
	pop3_server = 'pop.163.com'
	
	server = poplib.POP3(pop3_server)
	server.set_debuglevel(1)
	print(server.getwelcome().decode('utf8'))
	
	server.user(user_account)
	server.pass_(password)
	
	print("mail count: %d, Storage Size: %d" % (server.stat()[0], server.stat()[1]))
	
	resp, mails, octets = server.list()
	
	# 取最新一封邮件
	response_status, mail_msg_lines, octets = server.retr((len(mails)))
	print('邮件获取状态： %s' % response_status)
	print('原始邮件数据:\n %s' % mail_msg_lines)
	print('该封邮件所占字节大小: %d' % octets)
	
	msg_content = b'\r\n'.join(mail_msg_lines).decode('gbk')
	msg = Parser().parsestr(text=msg_content)
	print('解码后的邮件信息:\n%s' % msg)
	
	server.close()
	return msg


def get_mail_info(s):
	nickname, account = s.split(' ')
	# 获取字串的编码信息
	charset = nickname.split('?')[1]
	# print('编码：{}'.format(charset))
	nickname = nickname.split('?')[3]
	nickname = str(base64.decodebytes(nickname.encode(encoding=charset)), encoding=charset)
	account = account.lstrip('<')
	account = account.rstrip('>')
	return nickname, account


def get_details(msg):
	details = {}
	from_str = msg.get('From')
	from_nickname, from_account = get_mail_info(from_str)
	print(from_nickname, from_account)
	to_str = msg.get('To', "")
	to_nickname, to_account = get_mail_info(to_str)
	print(to_nickname, to_account)
	subject = msg.get('Subject')
	print(subject)


msg = get_parsed_msg()
get_details(msg)
parts = msg.get_payload()
content_type = parts[0].get_content_type()
content_charset = parts[0].get_content_charset()
content = parts[0].as_string().split('base64')[-1]
print('Content*********', decode_base64(content, content_charset))
content = parts[1].as_string().split('base64')[-1]
print('HTML Content:', decode_base64(content, content_charset))
