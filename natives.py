"""
This file contains structural functions required for basic/debug bot interaction on discord severs
and implements basic persistence.
eval, exec, aeval -> rank >=100
come, leave -> rank >= 25
"""

import pickle
import configparser
import os
import sys
import time


class PycChannel:
    rank = 25
    help_dict = {'py_come': 'bring 00Unit to channel', 'py_leave': 'remove 00Unit from channel'}

    def __init__(self, client, message):
        self.client = client
        self.message = message

    async def py_come(self):
        if self.message.channel.id in bot_vars['allowed_channels']:
            await self.client.send_message(self.message.channel, "channel already enabled")
        else:
            bot_vars['allowed_channels'].append(self.message.channel.id)
            await self.client.send_message(self.message.channel, 'channel enabled')

    async def py_leave(self):
        if self.message.channel.id in bot_vars['allowed_channels']:
            bot_vars['allowed_channels'].remove(self.message.channel.id)
            await self.client.send_message(self.message.channel, "channel disabled")
        else:
            await self.client.send_message(self.message.channel, "channel already disabled")

class PycCustom:
    rank = 50
    help_dict = {'py_add': 'Add a custom command', 'py_rem': 'remove a custom command', 'py_customlist':
                 'list custom commands'}

    def __init__(self, client, message):
        self.client = client
        self.message = message

    async def py_add(self, name, *cmd):
        try:
            bot_vars['custom_cmds'][name] = " ".join(cmd)
        except KeyError:
            bot_vars['custom_cmds'] = {name: " ".join(cmd)}

    async def py_rem(self, name):  # TODO: rest of PycCustom
        try:
            del bot_vars['custom_cmds'][name]
        except KeyError:
            await self.client.send_message(self.message.channel, "Error removing command: Command Not Found")

    async def py_customlist(self):
        await safe_send(self.message.channel, self.client, "\n".join(sorted([m for m in bot_vars['custom_cmds']])))


# ----------------------------------------------------------------------------------------------------------------------
# end of Channel class


class PycRoot:
    rank = 510
    help_dict = {'py_eval': 'chats eval(args)', 'py_aeval': 'awaits eval(args)', 'py_exec': 'exec(args)',
                 'py_callme': 'adds callsign', 'py_die': 'client.logout()', 'py_nocall': 'removes callsign'}

    def __init__(self, client, message):
        self.client = client
        self.message = message

    async def py_eval(self, *args):
        try:
            await self.client.send_message(self.message.channel, '```python\n' + str(eval(' '.join(args))) + '```')
        except Exception as lol:
            await self.client.send_message(self.message.channel, lol)

    async def py_aeval(self, *args):
        try:
            await eval(' '.join(args))
        except Exception as lol:
            await self.client.send_message(self.message.channel, lol)

    async def py_exec(self, *args):
        try:
            code = ' '.join(args)
            print(str(self.message.timestamp) + ' [' + self.message.author.name + '] in [' +
                  self.message.server.name + ']/[' + self.message.channel.name +
                  '] executed:\n--------------------------------\n' + code +
                  '\n--------------------------------\nwith output:')
            exec(code)
            print('\n')
            await self.client.send_message(self.message.channel, 'code executed')
        except Exception as lol:
            await self.client.send_message(self.message.channel, lol)

    async def py_callme(self, callsign):
        bot_vars['callsign'].append(str(callsign))
        await self.client.send_message(self.message.channel, 'I will now respond to ' + str(callsign))

    async def py_nocall(self, callsign):
        if callsign in bot_vars['callsign']:
            bot_vars['callsign'].remove(callsign)
            await self.client.send_message(self.message.channel, 'I will no longer respond to ' + str(callsign))
        else:
            await self.client.send_message(self.message.channel, 'Nobody calls me that :R')

    async def py_die(self):
        await self.client.send_message(self.message.channel, "Bye-bye")
        await self.client.logout()


# ----------------------------------------------------------------------------------------------------------------------
# end of Root class


async def safe_send(channel, client, message):
    if len(message) < 1990:
        await client.send_message(channel, message)
    else:
        while len(message) > 1990 and message.rfind("\n", 0, 1990) != -1:
            inx = message.rfind("\n", 0, 1990)
            await client.send_message(channel, message[:inx])
            message = message[inx:]
        await client.send_message(channel, message)


# command parser
# ----------------------------------------------------------------------------------------------------------------------
def parse(message):
    try:
        ratelimit = bot_vars['ratelimit']
    except KeyError:
        bot_vars['ratelimit'] = 1.0
        ratelimit = bot_vars['ratelimit']


    for callsign in bot_vars['callsign']:
        if message.content.startswith(callsign):
            try:
                if time.time() - bot_vars['ratetime'] < ratelimit:
                    print("{}{:>20}{:<10}{}{:<15}{}{}".format(time.strftime("%Y-%m-%d %H:%M:%S"), " RATELIMIT: ", message.author.name[:10], "| Channel: ", message.channel.name[:15], "| Msg: ", message.content))
                    if message.author.id != "132694825454665728":
                        return 'ratelimit', []
            except KeyError:
                bot_vars['ratetime'] = 0

            bot_vars['ratetime'] = time.time()
            cmd_args = message.content.replace(callsign, 'py', 1).split()
            cmd = '_'.join(cmd_args[0:2])
            args = [x for x in cmd_args[2:len(cmd_args)]]
            for asd in args:
                args[args.index(asd)] = \
                    args[args.index(asd)].replace('\\n', '\n').replace('\\t', '\t').replace('\\s', '\u0020')
            return cmd, args
        else:
            return 'wrong_callsign', []


# ------------------------------------------------------------------------------------------------------------------


# persistence module
# ----------------------------------------------------------------------------------------------------------------------
def save():
    with open('bot_vars.pickle', 'wb') as save_file:
        pickle.dump(bot_vars, save_file)
        save_file.close()


def load():
    try:
        with open('bot_vars.pickle', 'rb') as save_file:
            __builtins__['bot_vars'] = pickle.load(save_file)
            save_file.close()
    except IOError:
        admin1, admin2 = config['GENERAL']['adminID'], config['GENERAL']['adminID2']
        __builtins__['bot_vars'] = {'ranks': {admin1: 512, admin2: 512}, 'allowed_channels': [],
                                    'cmd_dict': {}, 'callsign': 'py', 'cmd_list': [], 'ratelimit': 1.0, 'ratetime': 0}
        save()


def reset():
    os.remove('bot_vars.pickle')
    load()

config = configparser.ConfigParser()
config.read('pymod.ini')
load()
# ----------------------------------------------------------------------------------------------------------------------
