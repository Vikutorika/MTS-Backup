# -*- coding: utf-8 -*-
import os
import re
from utils.parser import base_parser


class BungeecordParser(base_parser.BaseParser):
	NAME = os.path.basename(__file__).rstrip('.py')

	def __init__(self, parser_manager):
		super().__init__(parser_manager)
		self.STOP_COMMAND = 'end'

	def parse_server_stdout(self, text):
		result = self.parse_server_stdout_raw(text)

		# 09:00:02 [信息] Listening on /0.0.0.0:25565
		# 09:00:01 [信息] [Steve] -> UpstreamBridge has disconnected
		time_data = re.search(r'[0-9]*:[0-9]*:[0-9]* ', text).group()
		elements = time_data[0:-1].split(':')
		result.hour = int(elements[0])
		result.min = int(elements[1])
		result.sec = int(elements[2])

		text = text.replace(time_data, '', 1)
		result.logging_level = text.split(' ')[0][1:-1]
		# [信息] Listening on /0.0.0.0:25565
		# [信息] [Steve] -> UpstreamBridge has disconnected

		text = text.replace(re.match(r'\[.*\] ', text).group(), '', 1)
		# Listening on /0.0.0.0:25565
		# [Steve] -> UpstreamBridge has disconnected

		result.content = text
		return result

	def pre_parse_server_stdout(self, text):
		text = super().pre_parse_server_stdout(text)
		match = re.match(r'>*\r', text)
		if match is not None:
			text = text.replace(match.group(), '', 1)
		return text

	def parse_server_startup_done(self, info):
		# Listening on /0.0.0.0:25577
		return not info.is_user and re.fullmatch(r'Listening on /[0-9.]+:[0-9]+', info.content) is not None

	def parse_rcon_started(self, info):
		return self.parse_server_startup_done(info)

	def parse_server_stopping(self, info) -> bool:
		# Closing listener [id: 0x3acae0b0, L:/0:0:0:0:0:0:0:0:25565]
		return not info.is_user and re.fullmatch(r'Closing listener \[id: .+, L:[\d:/]+\]', info.content) is not None


def get_parser(parser_manager):
	return BungeecordParser(parser_manager)
