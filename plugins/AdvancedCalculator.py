# -*- coding: utf-8 -*-
from utils.rtext import *

HELP_MSG = '''
§7!!calc <expression> §6计算表达式
§7!!calc item <count> §6物品数转换堆叠数
§7!!calc item <box> <stack> <single> §6堆叠数转换物品数
§7!!calc color <red> <green> <blue> §610进制RGB转16进制
§7!!calc color <#HEX> §616十进制RGB转10进制'''


class Stack:
    single = 0
    stack = 0
    box = 0


def on_load(server, old):
    server.add_help_message('!!calc', '查看计算插件使用帮助')


def on_user_info(server, info):
    if not info.is_player or not info.content.startswith('!!calc'):
        return

    arg = info.content.split(' ')

    # !!calc
    if len(arg) == 1:
        server.reply(info, HELP_MSG)

    # !!calc <expression>
    elif len(arg) == 2:
        calc_expression(server, arg[1])

    # !!calc item <count>
    elif len(arg) in [3, 5] and arg[1] == 'item':
        calc_item(server, arg[2:])

    # !!calc color <red> <green> <blue>|<#HEX>
    elif len(arg) in [3, 5] and arg[1] == 'color':
        calc_color(server, arg[2:])
    else:
        server.reply(info, HELP_MSG)


def error_format(example):
    return f'§c格式错误! 例: §7{example}'


def calc_expression(server, exp):
    try:
        server.say(f'§7{exp}=§6{eval(exp)}')
    except (NameError, SyntaxError, ZeroDivisionError) as e:
        server.say(RText(f'§c计算 §6{exp} §c出错: §6{type(e).__name__}').h(e))


def calc_item(server, arg):
    if len(arg) == 1:
        count = arg[0]
        if not count.isdigit():
            server.say(error_format('!!calc item 1'))
        else:
            count = int(count)
        s = Stack()
        s.single = count % 64
        s.box = count // (64 * 27)
        s.stack = (count - s.box * 64 * 27) // 64
        server.say(RTextList(
            f'§6{count}§7个物品为',
            RText(f'{s.box}盒', color=RColor.yellow),
            RText(f'{s.stack}组', color=RColor.green),
            RText(f'{s.single}个', color=RColor.aqua)
        ))
    elif len(arg) == 3:
        try:
            arg = [int(i) for i in arg]
        except ValueError as e:
            return server.say(RText(error_format('!!calc item 1 0 1')).h(e))
        count = (arg[0] * 64 * 27) + (arg[1] * 64) + arg[2]
        server.say(RTextList(
            RText(f'{arg[0]}盒', color=RColor.yellow),
            RText(f'{arg[1]}组', color=RColor.green),
            RText(f'{arg[2]}个', color=RColor.aqua),
            f'§7为§6{count}§7个物品',
        ))


def calc_color(server, arg):
    server.logger.info(arg)

    def rgb_to_hex(red, green, blue):
        c = ''
        for color in (red, green, blue):
            color = int(color)
            if not (0 <= color <= 255):
                raise ValueError('Color must between 0-255')
            c += hex(color)[-2:].replace('x', '0').zfill(2)
        return c.upper()

    def hex_to_rgb(red, green, blue):
        rgb = []
        for i in (red, green, blue):
            color = int(i.lower(), 16)
            if not (0 <= color <= 255):
                raise ValueError('Color must between 00-ff')
            rgb.append(color)
        return rgb

    if len(arg) == 1:
        arg = arg[0]
        if not arg.startswith('#') or len(arg) != 7:
            return server.say(error_format('!!calc color #FF0000'))
        try:
            result = hex_to_rgb(arg[1:3], arg[3:5], arg[5:])
            server.say(f'§6{arg} §7-> §6{result}')
        except ValueError as e:
            server.say(RText(error_format('!!calc color 255 0 0')).h(e))
    elif len(arg) == 3:
        try:
            server.say(f'§6{[int(i) for i in arg]} §7-> §6#{rgb_to_hex(*arg)}')
        except (ValueError, TypeError) as e:
            server.say(RText(error_format('!!calc color 255 0 0')).h(e))