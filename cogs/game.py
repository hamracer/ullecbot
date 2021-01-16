import discord
import random
import sqlite3
from discord.ext import commands

conn = sqlite3.connect()

class gameCog(commands.Cog, name="game"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gen(self, ctx):

    @commands.command()
    async def gen(self, ctx):



def setup(bot):
    bot.add_cog(gameCog(bot))
    print('game cog loaded')

