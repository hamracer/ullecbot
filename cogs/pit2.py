import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
import math
from PIL import Image


class pit2Cog(commands.Cog, name="pit2"):

    def __init__(self, bot):
        self.bot = bot


    def getpowerlevel(self, ctx, dodger):
        #first we get the age of the account
        power = int(0)
        createdate = dodger.created_at
        createdate = createdate.date()
        todaydate = datetime.today().date()
        delta = relativedelta(todaydate, createdate)
        months = delta.years * 12 + delta.months
        power = power + months
        return power
        
    def dice(self):
        diceroll = random.randint(1,20)
        return diceroll

    @commands.command()
    async def bh(self, ctx):
        print('bullethell')
        dodger = ctx.author
        dodgerpl = self.getpowerlevel(ctx, dodger)

        modrole = discord.utils.get(ctx.guild.roles, name="mod")
        modnum = [m.name for m in modrole.members]

        inittitle = str(ctx.author.display_name + ' runs the gauntlet')
        embed = discord.Embed(color=0x9062d3, title = inittitle)
        embed.set_thumbnail(url=ctx.author.avatar.url)
        emby = await ctx.reply(embed=embed)

        rolls = len(modnum)
        dodgerac = int(14)
        i = 0
        print(rolls)
        modM = [m for m in modrole.members]
        hitcounter = int(0)
        while rolls > i:
            embed.clear_fields()
            print("checking power1")
            print(i)
            i += 1
            print(i)
            # mod powerlevel
            modpl = self.getpowerlevel(ctx, dodger=modM[i-1])
            print(modpl)
            modroll = int(self.dice())
        
            print(str(modpl) + " vs " + str(dodgerpl))

            embed.add_field(name=str(i) + " of " + str(rolls), value="", inline=False)
            print("starting")
            
            if modpl > dodgerpl:
                print("checking power2")
                modroll = modroll + 2
                print("checking power2")
            else:
                print("checking power3")
                modroll = modroll - 1
                print("checking power3")
            print(str(modroll) + " vs " + str(dodgerac))
            if modroll > dodgerac:
                print('hit')
                hitcounter += 1
                inittitle = str(ctx.author.display_name + ' has been hit ' + str(hitcounter) + " times")
                embed = discord.Embed(color=0x9062d3, title = inittitle)
                embed.set_thumbnail(url=modM[i-1].avatar.url)
                embed.set_footer(text=str(modroll) + "/20 > " + str(dodgerac))
                embed.add_field(name=str(modM[i-1].display_name) + " shoots " + str(dodger), value=str(dodger) + " has been hit!", inline=False)
                
            else: 
                print('dodge')
                inittitle = str(ctx.author.display_name + ' has been hit ' + str(hitcounter) + " times")
                embed = discord.Embed(color=0x9062d3, title = inittitle)
                embed.set_thumbnail(url=ctx.author.avatar.url)
                embed.set_footer(text=str(modroll) + "/20 ≤ " + str(dodgerac))
                embed.add_field(name=str(modM[i-1].display_name) + " shoots " + str(dodger), value=str(dodger) + " dodges!", inline=False)
            print("waiting")

            await asyncio.sleep(3)
            await emby.edit(embed=embed)
            print("END------------------------")

        await asyncio.sleep(3)
        if hitcounter > 0:
            pittimer = pow(2,int(hitcounter))
            inittitle = str(ctx.author.display_name + ' has been pitted for ' + str(pittimer) + " minutes")
            embed = discord.Embed(color=0x9062d3, title = inittitle)
            embed.set_thumbnail(url=ctx.author.avatar.url)
            embed.set_footer(text="2^" + str(hitcounter))
            await emby.edit(embed=embed)
        
        else:
            inittitle = str(ctx.author.display_name + ' has escaped the pit!')
            embed = discord.Embed(color=0x9062d3, title = inittitle)
            embed.set_thumbnail(url=ctx.author.avatar.url)
            embed.set_footer(text=ctx.author.display_name + " has escaped the pit x times")
            await emby.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(pit2Cog(bot))
    print('pit2 cog loaded')
