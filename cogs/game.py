import discord
import random
import sqlite3
from discord.ext import commands

conn = sqlite3.connect('db\game.db')
c = conn.cursor

#first time run




class gameCog(commands.Cog, name="game"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def firsttimesetup(self):
        try:
            c.execute('''CREATE TABLE players
                (id, name, hp, str, dex, int, con, wis, cha)''')
            print('table created')
        except:
            print('table not created')
            pass

    @commands.command()
    async def gen(self, ctx):
        user_id = ctx.author.id
        created = ctx.author.created_at.strftime("%b %d, %Y")
        joined = ctx.author.joined_at.strftime("%b %d, %Y")
        print(user_id)
        print(created)
        print(joined)



def setup(bot):
    bot.add_cog(gameCog(bot))
    print('game cog loaded')

