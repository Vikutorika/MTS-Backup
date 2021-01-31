def on_info(server,info):
    if info.content == '!!re':
        server.execute('kick {} §dReconnect'.format(info.player))