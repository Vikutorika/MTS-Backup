# -*- coding: utf-8 -*-
# v0.1.0

online_player = []
execute = False


def on_load(server, old_module):
    if server.is_server_running():
        if server.is_rcon_running():
            global online_player
            query = server.rcon_query('list')
            online_player = query.split(':')[1].replace(' ', '').split(',')
            while '' in online_player:
                online_player.remove('')
        else:
            global execute
            server.execute('list')
            execute = True


def on_server_startup(server):
    if server.is_rcon_running():
        global online_player
        query = server.rcon_query('list')
        online_player = query.split(':')[1].replace(' ', '').split(',')
        while '' in online_player:
            online_player.remove('')
    else:
        global execute
        server.execute('list')
        execute = True


def on_player_joined(server, player):
    online_player.append(player)


def on_info(server, info):
    # if info.content == '!!list':
    #     server.reply(info, '§c' + str(get_player_list()))
    global execute, online_player
    if execute and 'players online' in info.content:
        if info.source != 0 or info.is_user:
            return
        online_player = info.content.split(':')[1].replace(' ', '').split(',')
        execute = False
        while '' in online_player:
            online_player.remove('')


def on_player_left(server, player):
    if player in online_player:
        online_player.remove(player)


def check_online(player: str) -> bool:
    if player in online_player:
        return True
    else:
        return False


def get_player_list() -> list:
    return online_player
