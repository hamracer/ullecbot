import discord
from discord.ext import commands
import asyncpg

conn = asyncpg.connect('messages.db')
c = conn.cursor()

# try:
#     c.execute("""CREATE TABLE logs (
#         message_id integer unique,
#          author_id integer,
#           content text,
#            channel_id integer,
#             created_at text)""")
#     conn.commit()
#     # c.execute("""CREATE TABLE users (author_id integer unique)""")
#     # conn.commit()
#     print("tables created")
# except:
#     print("tables already created")



class logCog(commands.Cog, name="logs"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def getlogs(self, ctx):
        channel = ctx.channel
        count = 0
        activity = discord.Activity(name='you type', type=discord.ActivityType.watching)
        await self.bot.change_presence(activity=activity)
        await ctx.send("Starting... this might take a while")
        async for message in channel.history(limit=None):
            message_id = message.id
            author_id = message.author.id
            content = message.content
            channel_id = message.channel.id
            created_at = message.created_at
            try:
                c.execute("INSERT INTO logs VALUES(?,?,?,?,?)", (message_id, author_id, content, channel_id, created_at))
                conn.commit()
                count += 1
                print(count)
            except:
                pass
        await ctx.send("Logs collected")
def setup(bot):
    bot.add_cog(logCog(bot))
    print('logging cog loaded')

