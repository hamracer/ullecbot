import discord
from datetime import datetime
from discord.ext import commands
import re
import sqlite3

class autismCog(commands.Cog, name="autism"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def autism (self, ctx):
        conn = sqlite3.connect("configs/autism.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE autism (user NOT NULL PRIMARY KEY INT, posts INT)''')

        first = datetime.today().replace(day=1)
        channel = ctx.channel
        async for message in channel.history(after=first):
            author = message.author.id
            try:
                c.execute("""INSERT INTO autism VALUES (?,?)""",(author,int(1)))
            except:
                c.execute("""UPDATE austism SET posts = posts + 1 WHERE user = ?""",(author))
        conn.commit()

        query = c.execute("SELECT * FROM autism")
        data = c.fetchall()
        for d in data:
            print(d)

def setup(bot):
    bot.add_cog(autismCog(bot))
    print('autism cog loaded')
