# -*- coding: utf-8 -*-
from utils.server import Server
from utils import constant

if __name__ == '__main__':
	print('{} {} starting up'.format(constant.NAME_SHORT, constant.VERSION))
	print('{} is open source, u can find it here: https://github.com/Fallen-Breath/MCDReforged'.format(constant.NAME_SHORT))
	print('{} is still in development, it may not work well'.format(constant.NAME_SHORT))
	try:
		server = Server()
	except:
		print(f'Fail to initialize {constant.NAME_SHORT}')
		raise

	server.start()
