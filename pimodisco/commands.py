import random
import ast

from pimodisco import source_url, version as version__
from pimodisco.checks import authCheck

from discord import TextChannel
from discord.ext import commands


def setup_args(parser):
    pass

def setup(bot, args):
    @bot.command()
    async def version(ctx):
        """
        Says the currently active version of the bot.
        """
        await ctx.send('Version {}'.format(version__))

    @bot.command(aliases=['source'])
    async def code(ctx):
        """
        Prints a link to the bot's code.
        """
        await ctx.send("Here's a link to my source code: {}".format(source_url))