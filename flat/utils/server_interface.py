# -*- coding: utf-8 -*-
# An interface class for plugins to control the server
import time

from utils import tool
from utils.info import Info
from utils.server_status import ServerStatus


def format_string(data):
	return str(data).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


class ServerInterface:
	MCDR = True  # Identifier for plugins

	def __init__(self, server):
		self.__server = server
		self.logger = server.logger

	# the same as MCD 1.0

	def start(self, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called start()')
		self.__server.start_server()

	def stop(self, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called stop()')
		self.__server.stop(forced=False, new_server_status=ServerStatus.STOPPING_BY_PLUGIN)

	def execute(self, text, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called execute("{}")'.format(text))
		self.__server.send(text)

#	# without '\n' ending
#	# not suggest to use
#	def send(self, text, is_plugin_call=True):
#		if is_plugin_call:
#			self.logger.debug('Plugin called send("{}")'.format(text))
#		self.__server.send(text, ending='')

	def say(self, text, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called say("{}")'.format(text))
		self.execute('tellraw @a {{"text":"{}"}}'.format(format_string(text)), is_plugin_call=False)

	def tell(self, player, text, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called tell("{}", "{}")'.format(player, text))
		self.execute('tellraw {} {{"text":"{}"}}'.format(player, format_string(text)), is_plugin_call=False)

	# MCDR stuffs

	# if the server is running
	def is_server_running(self, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called is_server_running()')
		return self.__server.is_server_running()

	# if the server has started up
	def is_server_startup(self, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called is_running()')
		return self.__server.is_server_startup()

	# wait until the server is able to start
	def wait_for_start(self, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called wait_for_start()')
		while self.is_server_running(is_plugin_call=False):
			time.sleep(0.01)

	# restart the server
	def restart(self, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called restart()')
		self.stop(is_plugin_call=False)
		self.wait_for_start(is_plugin_call=False)
		self.start(is_plugin_call=False)

	# stop and exit the server
	def stop_exit(self, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called stop_exit()')
		self.__server.stop(forced=False)

	# return the permission level number the object has
	# the object can be Info instance or player name
	def get_permission_level(self, obj, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called get_permission_level("{}")'.format(obj))
		if type(obj) is Info:  # Info instance
			return self.__server.permission_manager.get_info_permission_level(obj)
		elif type(obj) is str:  # player name
			return self.__server.permission_manager.get_player_permission_level(obj)
		else:
			return None

	# if MCDR's rcon is running
	def is_rcon_running(self, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called is_rcon_running()')
		return self.__server.rcon_manager.is_running()

	# send command through rcon
	# return the result server returned from rcon
	# if rcon is not running return None
	def rcon_query(self, command, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called rcon_query("{}")'.format(command))
		return self.__server.rcon_manager.send_command(command)

	# reply to the info source, auto detects
	def reply(self, info, msg, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called reply("{}", "{}")'.format(info, msg))
		if info.is_player:
			self.tell(info.player, msg, is_plugin_call=False)
		else:
			for line in msg.splitlines():
				self.__server.logger.info(tool.clean_minecraft_color_code(line))

	# return the current loaded plugin instance. with this your plugin can access the same plugin instance as MCDR
	# parameter plugin_name is the name of the plugin you want
	# the plugin need to be in plugins/plugin_name.py
	# if plugin not found, return None
	def get_plugin_instance(self, plugin_name, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called get_plugin_instance("{}")'.format(plugin_name))
		plugin = self.__server.plugin_manager.get_plugin(plugin_name)
		if plugin is not None:
			plugin = plugin.module
		return plugin

	def add_help_message(self, prefix, message, is_plugin_call=True):
		if is_plugin_call:
			self.logger.debug('Plugin called add_help_message("{}", "{}")'.format(prefix, message))
		self.__server.command_manager.add_help_message(prefix, message)
