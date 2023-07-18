import discord
from discord.ext import commands
import json
import asyncio

#channel_id=[1031516168365801482,262371002577715201]
channel_id=[1031516168365801482,339155308767215618,262371002577715201]
calc_id=[1046770057876869171]

class powerCog(commands.Cog, name="fx"):
    def __init__(self, bot):
        self.bot = bot

    #months of server join + months of account age
    
async def setup(bot):
    await bot.add_cog(fxCog(bot))
    print('power cog loaded')
