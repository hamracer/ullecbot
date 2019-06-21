import discord
from discord.ext import commands
import sqlite3

conn = sqlite3.connect('messages.db')
c = conn.cursor()

try:
    c.execute("""CREATE TABLE messages (message_id integer, author text, message text)""")
except:
    print("DB already created")
conn.commit()


conn.close()



class logCog(commands.Cog, name="logs"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def getlogs(self, ctx):
        channel = ctx.channel

        async for message in channel.history():
            content = message.content




def setup(bot):
    bot.add_cog(logCog(bot))
    print('logging cog loaded')

