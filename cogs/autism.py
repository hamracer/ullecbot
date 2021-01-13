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
        userlist=[]
        count1=0
        conn = sqlite3.connect("configs/autism.db")
        c = conn.cursor()
        try:
            c.execute('''CREATE TABLE autism (user_id INTEGER PRIMARY KEY, posts INTEGER)''')
        except:
            print("table already exists")
        first = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        channel = ctx.channel
        print (first)
        async for message in channel.history(limit=None,after=first):
            count1 += 1
            print(count1)
            author = message.author.id
            try:
                c.execute("""INSERT INTO autism VALUES (?,?)""",(author,1))
            except:
                c.execute("UPDATE autism SET posts = posts + 1 WHERE user_id = ?", (author,))
        conn.commit()

        c.execute("SELECT * FROM autism ORDER BY posts DESC")
        data = list(c.fetchall())
        counting=0
        for d in data:
            counting+= 1
            username = ctx.guild.get_member(d[0])
            stringy = str(username) + ": " + str(d[1])
            userlist.append(stringy)
            print(counting)
        c.execute("DROP TABLE autism")
        for i in userlist:
            print(i)




def setup(bot):
    bot.add_cog(autismCog(bot))
    print('autism cog loaded')
