# -*- coding: utf-8 -*-
import shutil
import datetime
import os
import json as js
import platform
def read_config():
    with open("config/mirror.json") as json_file:
        config = js.load(json_file)
    return config
conf=read_config()

mirror_folder=conf['path']
remote_enable=conf['remote']['enable']
address=conf['remote']['address']
port=conf['remote']['port']
secret=conf['remote']['secret']
start_command=conf['command']
world=conf["world"]
source=[]
target=[]
mirror_started=False
flat_started=False
flat_folder='./flat/'

MCDRJudge=os.path.exists("{}MCDReforged.py".format(mirror_folder))

for i in range(len(world)):
    source.append('./server/{}'.format(world[i-1]))

if(MCDRJudge):
    for i in range(len(world)):
        target.append('{}/server/{}'.format(mirror_folder,world[i-1]))
else:
    for i in range(len(world)):
        target.append('{}/{}'.format(mirror_folder,world[i-1]))

if(remote_enable):
    from mcrcon import MCRcon


remote_info='''
§6[Mirror]§bRemote Information:
§5Rcon Address: §b{}
§5Rcon Port: §b{}
'''.format(address,port)

help_msg='''
§r======= §6Minecraft Mirror 镜像服插件 §r=======
§d本文件版本为MTS专用版~
使用§6!!mirror sync§r来同步主服务器到镜像服
使用§6!!mirror start§r来打开镜像服
使用§6!!flat start§r来打开超平坦服
使用§6!!flat init§r来初始化超平坦服
使用§6!!flat stop§r来关闭超平坦服（不推荐）
使用§6!!mirror info§r来查看rcon配置信息（管理员）
使用§6!!mirror stop§r来关闭镜像服（不推荐）
使用§6!!mirror status§r来查看镜像服务器是否开启
使用§6!!mirror rcon <command>§r来在镜像服中执行命令（管理员，无需输入/）
'''

SimpleOP=' {"text":"§6查看SimpleOP","clickEvent":{"action":"open_url","value":"https://github.com/GamerNoTitle/SimpleOP"}}'
StartStopHelper=' {"text":"§6查看StartStopHelper","clickEvent":{"action":"open_url","value":"https://github.com/MCDReforged-Plugins/StartStopHelper"}}'

def helpmsg(server,info):
    if info.is_player and info.content == '!!mirror':
        server.tell(info.player, help_msg)
        server.execute('tellraw '+ info.player + SimpleOP)
        server.execute('tellraw '+ info.player + StartStopHelper)

def sync(server,info):
    start_time=datetime.datetime.now()
    server.execute('save-all')
    server.say('§6[Mirror]正在同步到镜像服……')
    i=0
    try:
        while True:
            if(i>len(world)-1): break
            shutil.copytree(source[i],target[i])
            i=i+1
    except:
        try:
            while True:
                if(i>len(world)-1): break
                shutil.rmtree(target[i],True)
                shutil.copytree(source[i],target[i])
                i=i+1
        except Exception:
            while True:
                if(i>len(world)-1): break
                shutil.rmtree(target[i],True)
                ignore=shutil.ignore_patterns('session.lock')
                shutil.copytree(source[i],target[i],ignore=ignore)
                i=i+1

    end_time=datetime.datetime.now()
    server.say('§6[Mirror]同步完成！用时{}'.format(end_time-start_time))

def start(server,info):
    server.say('§6[Mirror]已执行镜像服开启操作！镜像服开启用时由服务器决定，一般为1~3分钟')
    if platform.system()=='Windows':
        os.system('cd {} && powershell {}'.format(mirror_folder,start_command))
    else:
        os.system('cd {} && {}'.format(mirror_folder,start_command))
    os.system('cd ..')
    global mirror_started
    mirror_started=False
    server.say('§6[Mirror]镜像服已关闭！')

def flat_start(server,info):
    server.say('§6[Mirror]已执行超平坦服务器开启操作！开启用时由服务器决定，一般为1~3分钟')
    if platform.system()=='Windows':
        os.system('cd {} && powershell {}'.format(flat_folder,start_command))
    else:
        os.system('cd {} && {}'.format(flat_folder,start_command))
    os.system('cd ..')
    global flat_started
    flat_started=False
    server.say('§6[Mirror]超平坦已关闭！')

def flat_init(server,info):
    start_time=datetime.datetime.now()
    shutil.rmtree('./flat/server/world',True)
    shutil.copytree('./flat/server/init','./flat/server/world')
    end_time=datetime.datetime.now()
    server.say('§6[Mirror]超平坦服务器初始化完成！用时{}'.format(end_time-start_time))

def command(server,info):
    if(conf['remote']['command']):
        if(server.get_permission_level(info)>2):
            try:
                with MCRcon(address,secret,port) as remote:
                    remote.command('/'+info.content[14:])
                    remote.disconnect()
            except Exception as e:
                server.tell(info.player,'§6[Mirror]§4连接错误：{}'.format(e))
        else:
            server.tell(info.player,'§6[Mirror]§4错误：权限不足')
    else:
        server.tell(info.player,' §6[Mirror]§4错误：rcon功能未开启！')

def stop(server,info):
    try:
        with MCRcon('127.0.0.1','bili33@WPX.Gamer',25595) as remote:
            remote.command('/stop')
            remote.disconnect()
    except Exception as e:
        server.tell(info.player,'§6[Mirror]§4连接错误：{}'.format(e))

def flat_stop(server,info):
    try:
        with MCRcon('127.0.0.1','bili33@WPX.Gamer',25595) as remote:
            remote.command('/stop')
            remote.disconnect()
    except Exception as e:
        server.tell(info.player,'§6[Mirror]§4连接错误：{}'.format(e))


def information(server,info):
    if(server.get_permission_level(info)>2):
        server.tell(info.player,remote_info)
    else:
        server.tell(info.player,"§6[Mirror]§4错误：权限不足")

def status(server,info):
    global mirror_started
    try:
        with MCRcon(address,secret,port) as remote:
            remote.command('/list')
            remote.disconnect()
        server.tell(info.player,'§6[Mirror]§l镜像服已开启！')
    except Exception:
        if mirror_started:
            server.tell(info.player,'§6[Mirror]§l镜像服正在启动中……')
        else:
            server.tell(info.player,'§4[Mirror]§l镜像服未开启！')

def flat_status(server,info):
    global mirror_started
    try:
        with MCRcon(address,secret,port) as remote:
            remote.command('/list')
            remote.disconnect()
        server.tell(info.player,'§6[Mirror]§l超平坦已开启！')
    except Exception:
        if flat_started:
            server.tell(info.player,'§6[Mirror]§l超平坦正在启动中……')
        else:
            server.tell(info.player,'§4[Mirror]§l超平坦未开启！')


def on_info(server,info):
    global flat_started
    if info.is_player and info.content == '!!mirror':
        helpmsg(server,info)

    if info.content == '!!mirror sync':
        sync(server,info)
    
    if info.content == '!!mirror start':
        global mirror_started
        if(mirror_started):
            server.tell(info.player,'§b[Mirror]镜像服已经开启，请不要重复执行指令！')
        else:
            mirror_started=True
            start(server,info)

    if('!!mirror rcon' in info.content):
        command(server,info)
    
    if(info.content=='!!mirror info'):
        information(server,info)

    if(info.content=='!!mirror stop'):
        stop(server,info)

    if(info.content=='!!mirror status'):
        status(server,info)

    if(info.content=='!!flat stop'):
        flat_stop(server,info)

    if(info.content=='!!flat status'):
        flat_status(server,info)
    
    if info.content == '!!flat start':
        if(flat_started):
            server.tell(info.player,'§b[Mirror]超平坦已经开启，请不要重复执行指令！')
        else:
            flat_started=True
            flat_start(server,info)

    if info.content == '!!flat init':
        if(flat_started):
            server.tell(info.player,'§6[Mirror]§4超平坦服务器已经开启，请先关闭服务器！')
        else:
            flat_init(server,info)

