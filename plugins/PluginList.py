import glob

plugins=[""]

def tell_message(server, info, plugins):
    msg='''
    §6[PluginList]
    §a本服务器已安装插件列表如下：
    {}
    '''.format(plugins)
    server.tell(info.player,msg)

def get_list():
    plugins = glob.glob('plugins/*.py')
    return plugins

def on_info(server,info):
    if info.content == '!!pl':
        plugins = get_list()
        tell_message(server, info, plugins)
