"""
This file contains structural functions required for basic/debug bot interaction on discord severs
and implements basic persistence.
eval, exec, aeval -> rank >=100
come, leave -> rank >= 25
"""

import pickle
import configparser
import os


class PycChannel:
    def __init__(self, client, message):
        self.client = client
        self.message = message
        self.rank = 25

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
# ----------------------------------------------------------------------------------------------------------------------
# end of Channel class


class PycHelp:
    def __init__(self, client, message):
        self.client = client
        self.message = message
        self.rank = 0

    async def py_help(self):
        listing = []
        for key in bot_vars['cmd_dict']:
            for thing in bot_vars['cmd_dict'][key]:
                listing.append(thing)
            helpmsg = 'Available commands are: ```\n' + '\n'.join(listing) + '```\nUse $x in the command to pass ' \
                                                                             'parameter x to a function that ' \
                                                                             'requires it.'
        await self.client.send_message(self.message.channel, helpmsg)
# ----------------------------------------------------------------------------------------------------------------------
# end of Help class


class PycRoot:
    def __init__(self, client, message):
        self.client = client
        self.message = message
        self.rank = 100

    async def py_eval(self, *args):
        try:
            await self.client.send_message(self.message.channel, '```' + str(eval(' '.join(args))) + '```')
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

# ----------------------------------------------------------------------------------------------------------------------
# end of Root class


# command parser
# ----------------------------------------------------------------------------------------------------------------------
def parse(message):
    cmd_args = message.content.split()
    cmd = '_'.join([y for y in cmd_args if '$' not in y])
    args = [x for x in cmd_args if '$' in x]
    for asd in args:
        args[args.index(asd)] = \
            args[args.index(asd)].replace('$', '').replace('\\n', '\n').replace('\\t', '\t').replace('\\s', '\u0020')
    return cmd, args

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
        __builtins__['bot_vars'] = {'ranks': {admin1: 512, admin2: 512}, 'allowed_channels': [], 'cmd_dict': {}}
        save()


def reset():
    os.remove('bot_vars.pickle')
    load()

config = configparser.ConfigParser()
config.read('pymod.ini')
load()
# ----------------------------------------------------------------------------------------------------------------------
