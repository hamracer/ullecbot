import discord
from discord.ext import commands
import json
import asyncio

#active channel list
channel_id=[562352225423458326]

#emoji list
loading = '<a:loading:902407104499974144>'
borpaspin = '<a:borpaspin:905835451204640829>'

async def spinner(id):



class cuemCog(commands.Cog, name="cuem"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cum(self, ctx):
        if ctx.channel.id in channel_id:
            await ctx.message.add_reaction(emoji=loading)
            
            spin=spinner(ctx.author.id)

            embed=discord.Embed(
                title='Slot Machine',
                description=spin
                )
            embed.add_field()
    
    
async def setup(bot):
    await bot.add_cog(cuemCog(bot))
    print('cuem cog loaded')

####
# The idea of this is to make a 5x5? slot machine or something similar
#
# spinner will spin to do dmg to a boss 
#