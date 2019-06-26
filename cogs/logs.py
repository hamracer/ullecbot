import discord
from discord.ext import commands
import asyncpg
import re
import datetime




class logCog(commands.Cog, name="logs"):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def getlogs(self, ctx):
            # connecting to the database
        conn = await asyncpg.create_pool(database="messages", user="postgres", password="password")        
            # getting the latest message in the db
        latestmessage = await conn.fetch("SELECT created_at FROM logs ORDER BY created_at desc LIMIT 1")
        latestmessage = latestmessage[0]['created_at']
        channel = ctx.channel
            # count used to check what message we are up to
        count = 0
        activity = discord.Activity(name='you type', type=discord.ActivityType.watching)
        await self.bot.change_presence(activity=activity)
        await ctx.send("Starting... this might take a while")
            # for every message in the channel 
        async for message in channel.history(limit=None, after=latestmessage):
            message_id = message.id
            author_id = message.author.id
            content = message.content
            channel_id = message.channel.id
            created_at = message.created_at
                # inserting every message into a row
            try:
                await conn.execute("INSERT INTO logs (message_id, author_id, content, channel_id, created_at) VALUES($1, $2, $3, $4, $5)",message_id, author_id, content, channel_id, created_at)
                count += 1
                print(count)
            except:
                # print("Already logged "+ str(message_id))
                pass

        await ctx.send("Logs collected")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def check(self, ctx, arg1, arg2):
            # lazy way of getting the user_id
        arg1 = arg1.strip("<@")
        try:
            arg1 = arg1.strip("!")
        except:
            pass
        userid = arg1.strip(">")
        userid = int(userid)
        emote = arg2.split(":")
        emotestr = emote[1]
        emotestr = ":"+emotestr+":"
        puser = self.bot.get_user(userid)
            # connection to db 
        conn = await asyncpg.create_pool(database="messages", user="postgres", password="password")

        print(puser)

        row = await conn.fetch("SELECT content FROM logs WHERE author_id = $1", puser.id)
        counter = 0
        async with ctx.channel.typing():
            for i in row:
                if emotestr in i['content']:
                    counter += 1
                    print("WE FOUND ONE")
                print(i)
            titlestring = puser.name + " has " + arg2 + "'d "+ str(counter) + " times"
            embed = discord.Embed(title=titlestring)
            embed.set_thumbnail(url=puser.avatar_url)
            await ctx.send(embed=embed)


        # except Exception as e:
        #     print('Exception: ' + str(e))
            

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def type(self, ctx):
        conn = await asyncpg.create_pool(database="messages", user="postgres", password="password")

        latestmessage = await conn.fetch("SELECT created_at FROM logs ORDER BY created_at desc LIMIT 1")
        print(type(latestmessage[0]['created_at']))


def setup(bot):
    bot.add_cog(logCog(bot))
    print('logging cog loaded')

