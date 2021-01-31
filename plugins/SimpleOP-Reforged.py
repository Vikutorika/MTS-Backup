# -*- coding: utf-8 -*-
import time
import re
import sys
from imp import load_source
PlayerInfoAPI = load_source('PlayerInfoAPI','./plugins/PlayerInfoAPI.py')
sys.path.append('plugins/')
msg='''
§6======== SimpleOP Reforged ========
§5一个由佛冷的SimpleOP魔改而来的小插件
§5魔改的目的是供自己使用，万物皆可魔改~
§5--GamerNoTitle
§4需要PlayerInfoAPI！
§6!!op 可以获取OP权限（无权限要求§4危险§6，本服禁用）
§6!!restart 可以重启服务器（有10s倒计时）
§6!!stop 可以关闭服务器（有10s倒计时）
§6!!save 可以手动保存服务器世界
§6!!sr sp 可以将自己的出生点设置为当前位置（黑曜石机调试必备）
§6!!sr where <player> 可以获取某位玩家的坐标
§6Being Developed...
§6===================================
'''
prefix='!!sr'

def on_load(server, old_module):
    server.add_help_message('!!sr', '§5获取SimpleOP-Reforged的使用方法')

def get_pos(server,player):
    PlayerInfoAPI = server.get_plugin_instance('PlayerInfoAPI')
    pos=None
    dim=None
    pos=PlayerInfoAPI.getPlayerInfo(server, player, 'Pos')
    dim=PlayerInfoAPI.getPlayerInfo(server, player, 'Dimension')
    if pos == None and dim == None:
        return None,None
    else: return pos,dim

def change_dim(dim):
    dimlist={
        "minecraft:overworld": 0,
        "minecraft:the_nether": -1,
        "minecraft:end": 1
    }
    try:
        changed_dim=dimlist[str(dim)]
    except:
        changed_dim=0
    return changed_dim

def on_info(server, info):
    waiting_time=10	# 在这里设置重启或关服等待的时间
    time_left=waiting_time
    message=info.content.split()
    if prefix in info.content or 'op' in info.content or 'deop' in info.content or 'restart' in info.content or 'stop' in info.content or 'save' in info.content:
        if info.content == '!!sr':
            server.tell(info.player, msg)
        
        if message[0]=='!!sr':
            if info.is_player and message[1] == 'where' and len(message)==3:
                player_for_search=message[2]
                position,Dimension=get_pos(server,player_for_search) 
                if position == None and Dimension == None:
                    server.tell(info.player,'玩家§b{}§r不在线'.format(player_for_search))
                else:
                    try:
                        Dimension=int(Dimension)
                    except:
                        Dimension=change_dim(Dimension)
                    where='玩家§b{}§r在[x: {}, y: {}, z: {}, dim: {}]'.format(player_for_search,int(position[0]),int(position[1]),int(position[2]),Dimension)
                    server.tell(info.player, where)
                    server.tell(player_for_search, '玩家§b{}§r正在寻找你,你将会被应用15秒的高亮效果'.format(info.player))
                    server.execute('effect give {} minecraft:glowing 15 0 true'.format(player_for_search))
                
            if info.is_player and message[1] == 'sp':
                position,Dimension=get_pos(server,info.player) 
                server.execute('spawnpoint ' + info.player + ' {} {} {}'.format(int(list(position)[0]),int(list(position)[1]),int(list(position)[2])))

        if info.is_player and info.content == '!!NOMOREOP':
            server.execute('op ' + info.player)

        if info.is_player and info.content == '!!deop':
            server.execute('deop ' + info.player)


        if info.content == '!!restart':
            restart_message=''
            while True:
                restart_message='Server will restart in {} second(s), please save your work!'.format(time_left)
                server.say(restart_message)
                if(time_left==0):
                    server.restart()
                    break
                else:
                    time.sleep(1)
                    time_left=time_left-1

        if info.content == '!!stop':
            stop_message=''
            while True:
                stop_message='Server will close in {} second(s), please save your work!'.format(time_left)
                server.say(stop_message)
                if(time_left==0):
                    server.stop_exit()
                    break
                else:
                    time.sleep(1)
                    time_left=time_left-1
                    
        if info.content == '!!save':
            server.execute('save-all')