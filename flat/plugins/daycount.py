# -*- coding: utf-8 -*-
import copy
import datetime

startday = datetime.datetime.strptime('2020-03-07', '%Y-%m-%d')

def onServerInfo(server, info):
  if info.isPlayer == 1:
    if info.content.startswith('!!day'):
      server.say('今天是这个服务器开服的第' + getday() + '天')

def on_info(server, info):
  info2 = copy.deepcopy(info)
  info2.isPlayer = info2.is_player
  onServerInfo(server, info2)

def getday():
  now = datetime.datetime.now()
  output = now - startday
  return str(output.days)

def on_load(server, old):
  server.add_help_message('!!day', '显示今天是开服第几天')