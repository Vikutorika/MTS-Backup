MCDReforged Plugin Document
---

[中文](https://github.com/Fallen-Breath/MCDReforged/blob/master/doc/plugin_cn.md)

Like MCDaemon, a MCDR plugin is a `.py` file locating in the `plugins/` folder. MCDR will automatically load every plugin inside this folder

There is a sample plugin named `sample_plugin.py` in the `plugins/` folder and you can check its content for reference

When the server has trigger specific event, MCDR will call relevant method of each plugin if the plugin has declared the method. MCDR will create a separated thread for the called method to run

| Method | When to call | Independent thread | Reference usage |
|---|---|---|---|
| on_load(server, old_module) | A plugin gets loaded | Yes | The new plugin inherits information from the old plugin |
| on_unload(server) | A plugin gets unloaded | Yes | Clean up or turn off functionality of the old plugin |
| on_info(server, info) | A new line is output from the stdout of the server, or a command is input from the console | Yes | Response to the information |
| on_player_joined(server, player) | A player joined the server | Yes | Response to player joining |
| on_player_left(server, player) | A player left the server | Yes | Response to player leaving |
| on_server_startup(server) | The server has started up such as vanilla server outputs `Done (1.0s)! For help, type "help"` | Yes | Initialize something |
| on_server_stop(server, return_code) | The server has, more precisely, server process has terminated | Yes | Process something related with the int type return_code parameter |
| on_mcdr_stop(server) | The server has stopped and MCDR is about to exit | No | Save data and release resources

Note: the plugin doesn't need to implement all methods above. Just implement what you need

Among them, the information of each parameter object is as follows：

## server

This is a object for the plugin to interact with the server. It belongs to the ServerInterface class in `utils/server_interface.py`

It has following constants:

| Constants | Type | Function |
|---|---|---|
| MCDR | bool | This constant is used to the plugin to determine whether it's running on MCDR. You can use `hasattr(server, 'MCDR')` to check

It has following variables:

| Variable | Type | Function |
|---|---|---|
| logger | logging.Logger | A logger of MCDRIt is better to use `server.logger.info (message)` instead of `print (message)` to output information to the console. [docs](https://docs.python.org/3/library/logging.html#logger-objects)

It also has these following methods:

**Server Control**

| Method | Function |
|---|---|
| start() | Start the server. Only works if the server has stopped |
| stop() | Use the specific command like `stop` to close the server. Only works if the server is running |
| wait_for_start() | Wait until the server is stopped, in other words, startable |
| restart() | Execute `stop()`、`wait_for_start()`、`start()` in order to restart the server |
| stop_exit() | Close the server and MCDR, in the other words, exit the program |
| is_server_running() | If the server (more precisely, server process) is running |
| is_server_startup() | If the server has started up |
| is_rcon_running() | Return a bool representing if the rcon is running |

**Text Interaction**

| Method | Function |
|---|---|
| execute(text) | Send a string `text` to the stdin of the server with a extra `\n` at the end |
| say(text) | Use `tellraw @a` to broadcast message `text` in the server |
| tell(player, text) | Use `tellraw <player>` to send message `text` to player `<player>` |
| reply(info, text) | Send a string `text` to the info source: if it's from a player calls `tell(info.player, text)`; if not uses MCDR's logger to info `text` to the console

If there special characters in string `text`, including `"`, `\\` and `\n`, MCDR will automatically escape them so you don't need to worry about them 

**Other**

| Method | Function |
|---|---|
| get_permission_level(obj) | Return a [integer](https://github.com/Fallen-Breath/MCDReforged#Permission) representing highest permission level the object `obj` has. `obj` can be a `Info` instance or a string representing a player name |
| rcon_query(command) | Send the command `command` via rcon to the server. Return a response string from the server. Return None if rcon stops or exception occurred |
| get_plugin_instance(plugin_name) | Return an instance of the loaded plugin located in `plugins/plugin_name.py`. Using this method instead of importing the plugin by yourself allows you to get the same instance as MCDR. If plugin not found returns None |
| add_help_message(prefix, message) | Add a help message with prefix `prefix` and message `message` to the `!!help` data of MCDR. The `!!help` data of MCDR will be reset before plugin reloading. **It is recommended to add relevant information in `on_load ()` method call** |

## info

This is a parsed information object. It belongs to the Info class in `utils/info.py`. It has the following attributes:

| Attribute | Content |
|---|---|
| hour | A integer，representing the hour when the message was sent. If there isn't it will be `None` |
| min | A integer，representing the minute when the message was sent. If there isn't it will be `None` |
| sec | A integer，representing the second when the message was sent. If there isn't it will be `None` |
| raw_content | An un-parsed raw message string |
| content | If the info is player's chat message, the value is the player's chat content. Otherwise, the value is a string after omitting the prefix information such as time / thread name from the original message string |
| player | If the info is player's chat message, the value is a string representing the player's name, otherwise `None` |
| source | An integer. `0` if the message is from the server's standard output stream;` 1` if it is from the console input |
| is_player | Equivalent to `player != None` |
| is_user | Equivalent to `source == 1 or is_player` |

### Samples

For the following message from the server's standard output：

`[11:10:00 INFO]: Preparing level "world"`

The attributes of the info object are:

| Attribute | Value |
|---|---|
| hour | 11 |
| min | 10 |
| sec | 0 |
| raw_content | `[09:10:00 INFO]: Preparing level "world"` |
| content | `Preparing level "world"` |
| player | None |
| source | 0 |
| is_player | False |
| is_user | False |

------

For the following message from the server's standard output：

`[09:00:00] [Server thread/INFO]: <Steve> Hello`

The attributes of the info object are:

| Attribute | Value |
|---|---|
| hour | 9 |
| min | 0 |
| sec | 0 |
| raw_content | `[09:00:00] [Server thread/INFO]: <Steve> Hello` |
| content | `Hello` |
| player | `Steve` |
| source | 0 |
| is_player | True |
| is_user | True |

### player

This is a string representing the name of the relevant player, such as `Steve`

### old_module

This is an instance of a module, which is used by the new plugin to inherit some necessary information from the old plugin after the plugin is reloaded. If its value is `None`, it means that this is the first time the MCDR has started loading the plugin

Related examples:

```
counter = 0

def on_load(server, old_module):
	global counter
    if old_module is not None:
        counter = old_module.counter + 1
    else:
        counter = 1
    server.logger.info(f'This is the {counter} time to load the plugin')
```

## Some tips for writing plugin

- The current working directory is the folder where MCDR is in. **DO NOT** change it since that will mess up everything
- For the `info` parameter in `on_info` don't modify it, just only read it
- If you want to import other plugin use `server.get_plugin_instance()` instead so the plugin instance you get is the same as the one MCDR uses
- Call `server.add_help_message()` in `on_load()` to add some necessary tips for your plugin so the player can use `!!help` command to know about your plugin
- Keep the environment clean. Store your data files in a custom folder in `plugins/`, your config file in `config/` folder and your log file in `log/` folder will be a good choice
- `on_mcdr_stop()` allows you to have as many time as you want to save your data. Be carefully, don't enter an endless loop, MCDR is waiting for you to exit

## Porting MCDaemon's plugin to MCDR

1. Modify the code of the old plugin that only works on python2 to be able to run on python3 and install required python modules
2. Update the variable / method name to the name of the MCDR, such as changing `onServerInfo` to` on_info` and `isPlayer` to` is_player`
3. MCDR also calls `on_info` when something has input from the console. Pay attention to whether the plugin is compatible with this situation

A lazy way to do that is to add such method below at the end of the old plugin after solving python3 compatibility issues:

```
import copy

def on_load(server, old):
	onServerStartup(server)

def on_player_joined(server, player):
	onPlayerJoin(server, player)

def on_player_left(server, player):
	onPlayerLeave(server, player)

def on_info(server, info):
	info2 = copy.deepcopy(info)
	info2.isPlayer = info2.is_player
	onServerInfo(server, info2)
```
