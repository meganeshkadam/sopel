# coding=utf-8
"""
testsystemsearch.py - Based on rhos/
Copyright © 2016, Sachin Patil, <psachin@redhat.com>
Licensed under the Eiffel Forum License 2.

This module depends on https://gitlab.com/pbandark/test_system_search/client/client.py
"""
from __future__ import unicode_literals, absolute_import, print_function, division
import requests
import sopel.module
from sopel.formatting import bold as bold_text
from sopel.logger import get_logger
from sopel.manage_systems.bot_client import IRCBot

LOGGER = get_logger(__name__)

# TODO: Should go in sopel config
rhos = IRCBot('localhost', '8000', 'rhos')

@sopel.module.commands('tss', 'testsystemsearch')
def search_system(bot, trigger):
    """
    Manage systems
    --------------
    Examples:

    Display unused systems:               .tss
    Display (used + unused) systems:      .tss --all
    Display in-use systems:               .tss --in-use
    Display RHOS 7 systems:               .tss 7
    Show detail of system with id 3:      .tss --detail 3
    Reserve system with id 7:             .tss --reserve 7 psachin@redhat.com
    Release system for others to use:     .tss --release 7
    """
    user_input = trigger.group().split()

    arg_count = len(user_input)

    if arg_count == 2:
        try:
            arg_one = user_input[1]

            if arg_one.startswith('--') and arg_one == '--all':
                bot.reply("Sending you list of ALL systems in a private message")
                for system in rhos.all_versions():
                    bot.say(system, trigger.nick)
            elif arg_one.startswith('--') and arg_one == '--in-use':
                bot.reply("Sending you list of in-use systems in a private message")
                for system in rhos.version(in_use=True):
                    bot.say(system, trigger.nick)
            elif arg_one.startswith('--') and arg_one not in ['--in-use', '--all']:
                bot.reply("{} required additional arguments".format(arg_one))
            else:
                bot.reply("Sending you list of systems(with RHOSP" +
                          " version {}) in a private message".format(user_input[1]))
                for system in rhos.version(version=arg_one):
                    bot.say(system, trigger.nick)
        except:
            pass
    elif arg_count == 3:
        try:
            arg_one = user_input[1]
            arg_two = user_input[2]

            if arg_one.startswith('--') and arg_one == '--detail':
                bot.say(rhos.detail(arg_two))
            if arg_one.startswith('--') and arg_one == '--release':
                bot.say(rhos.release(arg_two))
        except:
            pass
    elif arg_count == 4:
        arg_one = user_input[1]
        arg_two = user_input[2]
        arg_three = user_input[3]

        if arg_one.startswith('--') and arg_one == '--reserve':
            if '@' in arg_three:
                bot.reply("System is reserved for you. Sending you credentials in a private message")
                bot.say(rhos.reserve(arg_two, arg_three), trigger.nick)
            else:
                bot.say("Error: Invalid email-id")
    else:
        bot.reply("Sending you list of (unused)systems in a private message")
        for system in rhos.version():
            bot.say(system, trigger.nick)


if __name__ == "__main__":
    from sopel.test_tools import run_example_tests
    run_example_tests(__file__)
