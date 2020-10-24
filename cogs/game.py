import discord
import random
import sqlite3
from discord.ext import commands

conn = sqlite3.connect('db\game.db')
c = conn.cursor

#first time run

try:
    c.execute('''CREATE TABLE players
                (id, name, hp, str, dex, int, con, wis, cha)''')
                
except Exception as e:
            print('{} cannot be loaded. [{}]'.format(load, e))


class gameCog(commands.Cog, name="game"):
    def __init__(self, bot):
        self.bot = bot



     @commands.command()
    async def gen(self, ctx):



def setup(bot):
    bot.add_cog(gameCog(bot))
    print('game cog loaded')

