# -*- coding: utf-8 -*-

import os
import json
import time
import copy

PluginName = 'CarpetFeatureHelper'
Prefix = '!!carpet'
ConfigFileFolder = 'config/'
ConfigFilePath = ConfigFileFolder + PluginName + '.json'
LogFileFolder = 'log/'
LogFilePath = LogFileFolder + PluginName + '.log'
HelpMessage = '''------MCD ''' + PluginName + ''' v1.1------
一个自助开关指定carpet mod特性的插件
§a【指令说明】§r
§7''' + Prefix + ''' §r显示帮助信息
§7''' + Prefix + ''' query §6[feature]§7 §r显示§6[feature]§r的开关状态
§7''' + Prefix + ''' set §6[feature]§e true §r将§6[feature]§r设为§e打开
§7''' + Prefix + ''' set §6[feature]§e false §r将§6[feature]§r设为§e关闭
§7''' + Prefix + ''' list §r列出所有可用控制的特性
'''
DefaultConfigFile = '''{
	"availableFeatures":
	[
	]
}'''

emptyQueringStuff = ('', '', False)  # feature, info.player, info.isPlayer
queringStuff = emptyQueringStuff


def printMessage(server, info, msg, istell=True):
	for line in msg.splitlines():
		if info.isPlayer:
			if istell:
				server.tell(info.player, line)
			else:
				server.say(line)
		else:
			print(line)


def printLog(msg):
	if not os.path.exists(LogFileFolder):
		os.makedirs(LogFileFolder)
	if not os.path.exists(LogFilePath):
		with open(LogFilePath, 'w') as f:
			pass
	with open(LogFilePath, 'a') as logfile:
		logfile.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ': ' + msg + '\n')


def getAvailableFeatures():
	if not os.path.exists(ConfigFileFolder):
		os.makedirs(ConfigFileFolder)
	if not os.path.exists(ConfigFilePath):
		with open(ConfigFilePath, 'w') as f:
			f.write(DefaultConfigFile)
	with open(ConfigFilePath, 'r') as f:
		js = json.load(f)
		return js["availableFeatures"]


def queryFeatureStats(server, info, cmd):
	if cmd not in getAvailableFeatures():
		printMessage(server, info, '该特性不存在或不可操控！')
		return
	server.execute('carpet ' + cmd)
	global queringStuff
	queringStuff = (cmd, info.player, info.isPlayer)


def setFeature(server, info, cmd, arg):
	if cmd not in getAvailableFeatures():
		printMessage(server, info, '该特性不存在或不可操控！')
		return
	server.execute('carpet ' + cmd + ' ' + arg)
	printLog((info.player if info.isPlayer else '控制台') + '将' + cmd + '设置为了' + arg)
	printMessage(server, info, '已将§6' + cmd + '§r设置为§e' + arg)


def listFeature(server, info):
	lst = getAvailableFeatures()
	printMessage(server, info, '可操控的特性列表如下：')
	for i in lst:
		printMessage(server, info, '§6' + str(i) + '§r')


def respondCarpetReply(server, info):
	global queringStuff
	if info.isPlayer:
		return False
	tmpInfo = info
	tmpInfo.player = queringStuff[1]
	tmpInfo.isPlayer = queringStuff[2]
	ret = False
	if info.content == queringStuff[0] + ' is set to: true':
		printMessage(server, tmpInfo, '特性§6' + queringStuff[0] + '§r已开启')
		ret = True
	if info.content == queringStuff[0] + ' is set to: false':
		printMessage(server, tmpInfo, '特性§6' + queringStuff[0] + '§r已关闭')
		ret = True
	if ret:
		queringStuff = emptyQueringStuff
	return ret


def onServerInfo(server, info):
	if respondCarpetReply(server, info):
		return
	content = info.content
	if not info.isPlayer and content.endswith('<--[HERE]'):
		content = content.replace('<--[HERE]', '')

	command = content.split()
	if len(command) == 0 or command[0] != Prefix:
		return
	del command[0]

	if len(command) == 0:
		printMessage(server, info, HelpMessage)
		return

	cmdLen = len(command)
	# query
	if cmdLen == 2 and command[0] == 'query':
		queryFeatureStats(server, info, command[1])
	# set
	elif cmdLen == 3 and command[0] == 'set' and command[2] in ['true', 'false']:
		setFeature(server, info, command[1], command[2])
	# list
	elif cmdLen == 1 and command[0] == 'list':
		listFeature(server, info)
	else:
		printMessage(server, info, '参数错误！请输入§7' + Prefix + '§r以获取插件帮助')


def on_info(server, info):
	info2 = copy.deepcopy(info)
	info2.isPlayer = info2.is_player
	onServerInfo(server, info2)


def on_load(server, old):
	server.add_help_message(Prefix, '开关地毯mod特性/功能')