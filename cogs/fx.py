import discord
from discord.ext import commands
import json
import asyncio

#channel_id=[1031516168365801482,262371002577715201]
channel_id=[1031516168365801482,339155308767215618,262371002577715201]
calc_id=1046770057876869171

class fxCog(commands.Cog, name="fx"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in channel_id and "//twitter.com" in message.content:
            split = message.content.strip().split('/')
            # check if proper link
            if split[0] in ['http:', 'https:'] and split[1] == '' and split[2] == 'twitter.com' and ' ' not in split[3] and split[4] == 'status' and ' ' not in split[5]:
                print('detected twitter message') 
                if len(message.embeds) > 0 and 'video' in message.embeds[0].to_dict():
                    try: await message.channel.send(message.author + ": " + message.content.strip().replace('twitter.com', 'vxtwitter.com'))
                    except: pass # in case of lack of perm
                    try: await message.delete()
                    except: pass # in case of lack of perm
    
    
async def setup(bot):
    await bot.add_cog(fxCog(bot))
    print('fx cog loaded')
