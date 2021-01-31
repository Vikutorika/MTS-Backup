# -*- coding: utf-8 -*-
import locale
import logging
import sys
import time
import traceback
from subprocess import Popen, PIPE, STDOUT
from threading import Lock

from utils import config, constant, logger, tool
from utils.command_manager import CommandManager
from utils.parser_manager import ParserManager
from utils.permission_manager import PermissionManager
from utils.plugin_manager import PluginManager
from utils.rcon_manager import RconManager
from utils.language_manager import LanguageManager
from utils.server_status import ServerStatus
from utils.server_interface import ServerInterface
from utils.update_helper import UpdateHelper


class Server:
	def __init__(self):
		self.console_input_thread = None
		self.process = None  # the process for the server
		self.server_status = ServerStatus.STOPPED
		self.flag_interrupt = False  # ctrl-c flag
		self.flag_rcon_startup = False  # set to True after server startup. used to start the rcon server
		self.starting_server_lock = Lock()  # to prevent multiple start_server() call

		# will be assigned in reload_config()
		self.encoding_method = None
		self.decoding_method = None

		self.logger = logger.Logger(self, constant.NAME_SHORT)
		self.logger.set_file(constant.LOGGING_FILE)
		self.server_logger = logger.ServerLogger('Server')
		self.language_manager = LanguageManager(self, constant.LANGUAGE_FOLDER)
		self.config = config.Config(self, constant.CONFIG_FILE)
		self.rcon_manager = RconManager(self)
		self.parser_manager = ParserManager(self)
		self.load_config()
		self.reactors = self.load_reactor(constant.REACTOR_FOLDER)
		self.server_interface = ServerInterface(self)
		self.command_manager = CommandManager(self)
		self.plugin_manager = PluginManager(self, constant.PLUGIN_FOLDER)
		self.load_plugins()
		self.permission_manager = PermissionManager(self, constant.PERMISSION_FILE)
		self.update_helper = UpdateHelper(self)
		self.update_helper.check_update_start()

	# Translate info strings

	def translate(self, text, *args):
		result = self.language_manager.translate(text).strip()
		if len(args) > 0:
			result = result.format(*args)
		return result

	def t(self, text, *args):
		return self.translate(text, *args)

	# Loaders

	def load_config(self):
		self.config.read_config()

		self.language_manager.load_languages()
		self.language_manager.set_language(self.config['language'])
		self.logger.info(self.t('server.load_config.language_set', self.config['language']))

		self.logger.set_level(logging.DEBUG if self.config['debug_mode'] else logging.INFO)
		if self.config['debug_mode']:
			self.logger.info(self.t('server.load_config.debug_mode_on'))

		self.parser_manager.load_parser(constant.PARSER_FOLDER, self.config['parser'])
		self.logger.info(self.t('server.load_config.parser_set', self.config['parser']))

		self.encoding_method = self.config['encoding'] if self.config['encoding'] is not None else sys.getdefaultencoding()
		self.decoding_method = self.config['decoding'] if self.config['decoding'] is not None else locale.getpreferredencoding()
		self.logger.info(self.t('server.load_config.encoding_decoding_set', self.encoding_method, self.decoding_method))

		self.connect_rcon()

	def load_plugins(self):
		self.logger.info(self.plugin_manager.refresh_all_plugins())

	def load_reactor(self, folder):
		reactors = []
		for file in tool.list_file(folder, '.py'):
			module = tool.load_source(file)
			if hasattr(module, 'get_reactor') and callable(module.get_reactor):
				reactors.append(module.get_reactor(self))
		return reactors

	# MCDR server

	def is_server_running(self):
		return self.process is not None

	def is_server_startup(self):
		return self.flag_rcon_startup

	def set_server_status(self, status):
		self.server_status = status
		self.logger.debug('Server status has set to "{}"'.format(status))

	def start_server(self) -> bool:
		"""
		try to start the server process
		return True if the server process has started successfully
		return False if the server is already running or start_server has been called by other

		:return: a bool as above
		"""
		acquired = self.starting_server_lock.acquire(blocking=False)
		if not acquired:
			return False
		try:
			if self.is_server_running():
				self.logger.warning(self.t('server.start_server.start_twice'))
				return False
			try:
				start_command = self.config['start_command']
				self.logger.info(self.t('server.start_server.starting', start_command))
				self.process = Popen(start_command, cwd=self.config['working_directory'], stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True)
			except:
				self.logger.error(self.t('server.start_server.start_fail'))
				self.logger.error(traceback.format_exc())
				return False
			else:
				self.set_server_status(ServerStatus.RUNNING)
				self.logger.info(self.t('server.start_server.pid_info', self.process.pid))
				return True
		finally:
			self.starting_server_lock.release()

	def start(self):
		"""
		try to start the server. if succeeded the console thread will start and MCDR will start ticking

		:return: a bool, if the server start up try succeeds
		"""
		if not self.start_server():
			return False
		if not self.config['disable_console_thread']:
			if self.console_input_thread is None or not self.console_input_thread.is_alive():
				self.logger.debug('Console thread starting')
				self.console_input_thread = tool.start_thread(self.console_input, (), 'Console')
		else:
			self.logger.info('Console thread disabled')
		self.run()
		return True

	def stop(self, forced=False, new_server_status=ServerStatus.STOPPING_BY_ITSELF):
		"""
		stop the server

		:param forced: an optional bool. If it's False (default) MCDR will stop the server by sending the STOP_COMMAND from the
		current parser. If it's True MCDR will just kill the server process
		:param new_server_status: an optional ServerStatus object, the new server status MCDR will be set to
		default is STOPPING_BY_ITSELF, which will cause MCDR to exit after server has stopped
		set it to STOPPING_BY_PLUGIN to prevent MCDR exiting
		:return:
		"""
		self.set_server_status(new_server_status)
		if not self.is_server_running():
			self.logger.warning(self.t('server.stop.stop_twice'))
		else:
			if not forced:
				try:
					self.send(self.parser_manager.get_stop_command())
				except:
					self.logger.error(self.t('server.stop.stop_fail'))
					forced = True
			if forced:
				self.process.kill()
				self.logger.info(self.t('server.stop.process_killed'))

	def send(self, text, ending='\n'):
		"""
		send a text to server's stdin if the server is running
		:param text: a str or a bytes you want to send. if text is a str then it will attach the ending parameter to its
		back
		:param ending: the suffix of a command with a default value \n
		:return: None
		"""
		if type(text) is str:
			text = (text + ending).encode(self.encoding_method)
		if self.is_server_running():
			self.process.stdin.write(text)
			self.process.stdin.flush()
		else:
			self.logger.warning(self.t('server.send.send_when_stoped'))

	def receive(self):
		"""
		try to receive a str from server's stdout. This will block the thread
		if server has stopped it will wait up to 10s for the server process to exit and then set the server status
		to STOPPING_BY_ITSELF if the old server status is RUNNING

		:return: the received str, or None
		"""
		while True:
			try:
				text = next(iter(self.process.stdout))
			except StopIteration:  # server process has stopped
				for i in range(100):
					if self.process.poll() is not None:
						break
					time.sleep(0.1)
					if i % 10 == 0:
						self.logger.info(self.t('server.receive.wait_stop'))
				else:
					self.process.kill()
					time.sleep(1)
				if self.server_status is ServerStatus.RUNNING:
					self.set_server_status(ServerStatus.STOPPING_BY_ITSELF)
				return None
			else:
				try:
					text = text.decode(self.decoding_method)
				except:
					self.logger.error(self.t('server.receive.decode_fail', text))
					raise
				return text.rstrip().lstrip()

	def on_server_stop(self):
		return_code = self.process.poll()
		self.logger.info(self.t('server.on_server_stop.show_stopcode', return_code))
		self.process = None
		self.flag_rcon_startup = False
		if self.server_status == ServerStatus.STOPPING_BY_ITSELF:
			self.logger.info(self.t('server.on_server_stop.stop_by_itself'))
			self.set_server_status(ServerStatus.STOPPED)
		self.plugin_manager.call('on_server_stop', (self.server_interface, return_code))

	def tick(self):
		"""
		ticking MCDR: try to receive a new line from server's stdout and parse / display / process the text

		:return: None
		"""
		text = self.receive()
		if text is None:  # server process has been terminated
			self.on_server_stop()
			return

		try:
			text = self.parser_manager.get_parser().pre_parse_server_stdout(text)
		except:
			self.logger.warning(self.t('server.tick.pre_parse_fail'))
		self.server_logger.info(text)

		try:
			parsed_result = self.parser_manager.get_parser().parse_server_stdout(text)
		except:
			self.logger.debug('Fail to parse text "{}" from stdout of the server, using raw parser'.format(text))
			for line in traceback.format_exc().splitlines():
				self.logger.debug('    {}'.format(line))
			parsed_result = self.parser_manager.get_parser().parse_server_stdout_raw(text)
		else:
			self.logger.debug('Parsed text from server stdin:')
			for line in parsed_result.format_text().splitlines():
				self.logger.debug('    {}'.format(line))
		self.react(parsed_result)

	def run(self):
		"""
		the main loop of MCDR
		:return: None
		"""
		while self.server_status != ServerStatus.STOPPED:
			try:
				if self.is_server_running():
					self.tick()
				else:
					time.sleep(0.01)
			except KeyboardInterrupt:
				self.flag_interrupt = True
			except:
				if not self.flag_interrupt:
					self.logger.error(self.t('server.run.error'))
					self.logger.error(traceback.format_exc())
					self.stop()
				break
		# stop MCDR
		try:
			if self.flag_interrupt:
				self.logger.info(self.t('server.run.user_interrupted'))
			else:
				self.logger.info(self.t('server.run.server_stop'))
			self.plugin_manager.call('on_mcdr_stop', (self.server_interface,), wait=True)
			self.logger.info(self.t('server.run.bye'))
		except:
			self.logger.error(self.t('server.run.stop_error'))
			self.logger.error(traceback.format_exc())

	def console_input(self):
		"""
		the thread for processing console input
		:return: None
		"""
		while True:
			try:
				text = input()
				try:
					parsed_result = self.parser_manager.get_parser().parse_console_command(text)
				except:
					self.logger.error(self.t('server.console_input.parse_fail', text))
					self.logger.error(traceback.format_exc())
				else:
					self.logger.debug('Parsed text from console input:')
					for line in str(parsed_result).splitlines():
						self.logger.debug('    {}'.format(line))
					self.react(parsed_result)
			except (KeyboardInterrupt, EOFError, SystemExit, IOError) as e:
				self.logger.debug('Exception {} {} caught in console_input()'.format(type(e), e))
				self.stop(forced=self.flag_interrupt)
				self.flag_interrupt = True
			except:
				self.logger.error(self.t('server.console_input.error'))
				self.logger.error(traceback.format_exc())

	def react(self, info):
		"""
		react to a parsed info
		:param info: the info instance you want to react to
		:return: None
		"""
		for reactor in self.reactors:
			try:
				reactor.react(info)
			except Exception as e:
				self.logger.error(self.t('server.react.error', type(reactor).__name__))
				self.logger.error(traceback.format_exc())
				if e is KeyboardInterrupt:
					raise

	def connect_rcon(self):
		self.rcon_manager.disconnect()
		if self.config['enable_rcon'] and self.is_server_startup():
			self.rcon_manager.connect(self.config['rcon_address'], self.config['rcon_port'], self.config['rcon_password'])
