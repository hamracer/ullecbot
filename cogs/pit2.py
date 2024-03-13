import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime,date
from dateutil.relativedelta import relativedelta


class pit2Cog(commands.Cog, name="pit2"):

    def __init__(self, bot):
        self.bot = bot


    def getpowerlevel(self, ctx, dodger):
        #first we get the age of the account
        print('westart')
        power = int(0)
        print(power)
        createdate = dodger.created_at
        createdate = createdate.date()
        todaydate = datetime.today().date()
        delta = relativedelta(todaydate, createdate)
        months = delta.years * 12 + delta.months
        power = power + months
        print(power)
        #nitro?
        role = discord.utils.find(lambda r: r.name == 'Nitrocucks', ctx.message.guild.roles)
        if role in dodger.role:
            power = power + int(50)
            print("in nitrocucks")
            print(power)    
        else:
            print("no nitro")
            print(power)    
        return power
        
        

    @commands.command()
    async def bullethell(self, ctx):
        print('bullethell')
        dodger = ctx.author
        print(dodger.name)
        powerlevel = self.getpowerlevel(ctx, dodger)
        print(powerlevel)
        
    @commands.command()
    async def ls(self, ctx):
        print('starting')
        channel = discord.utils.get(ctx.guild.channels, name='starboard')
        sblist = []
        if channel:
            print('starboard exists')
            sblist = await channel.history(limit=100).flatten()
            print('final')
            print(sblist)
        else:
            print('does not exist')


async def setup(bot):
    await bot.add_cog(pit2Cog(bot))
    print('pit2 cog loaded')
