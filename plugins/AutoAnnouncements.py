import time

unloaded=False
prefix='§d[定时公告]§r'
ANN=[
    '§6打开各种机器前，请先使用§b!!qb make§6进行备份！',
    '§6如果机器炸膛，请使用§b!!qb back§6然后输入§b!!qb confirm§6进行回档',
    '§6建筑设计和红石机器设计可以调用镜像服，使用§b!!mirror§6来获取镜像服的相关使用方式',
    '§6如果不知道想要去的地方在哪里，可以使用§b!!wp§6从共享路径点中获取路径点',
    '§6可以在聊天栏输入§b!!help§6获取各个插件的使用指令'
]

msg='''§dMTS特供自动公告插件
§6如果不再需要本插件，请使用§b!!MCDR§6指令进行卸载！
以下是公告列表：
{}
'''.format(ANN)

def on_load(server,old_modules):
    global unloaded
    i=0
    while True:
        time.sleep(300)
        if(unloaded):
            break
        server.say(prefix+ANN[i])
        i=i+1
        if i==len(ANN):
            i=0
    
def on_info(server,info):
    if info.content=='!!ann':
        server.tell(info.player, msg)

def on_unload(server):
    global unloaded
    unloaded=True
