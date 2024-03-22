import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
import os
import psycopg
import psycopg_pool
from dotenv import load_dotenv

path=str(os.getcwd()) + '/configs/.env'
load_dotenv(override=True,dotenv_path=path)
connection_string = os.getenv('DATABASE_URL')
pool = psycopg_pool.AsyncConnectionPool(connection_string)

class pit2Cog(commands.Cog, name="pit2"):

    def __init__(self, bot):
        self.bot = bot
        


    async def openpool(self):
        try:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT NOW();')
                    time = await cur.fetchone()
                    await cur.execute('SELECT version();')
                    version = await cur.fetchone()
                    print('Current time:', time)
                    print('PostgreSQL version:', version)
        except:
            print('something went wrong tehe')



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
    @commands.has_role("cumdev")
    async def test(self, ctx):
        await self.openpool()

    @commands.command()
    @commands.has_role("cumdev")
    async def ct(self, ctx):
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("CREATE TABLE pit2 (userid integer PRIMARY KEY, hits integer, clears integer, kills integer)")
                print("table created")



    @commands.command()
    async def bh(self, ctx):
        print('bullethell')
        dodger = ctx.author
        userid = ctx.author.id
        dodgerpl = self.getpowerlevel(ctx, dodger)
        #id check
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute("SELECT * FROM pit2 WHERE userid=?",(userid))

                except:
                    await cur.execute("INSERT INTO pit2  VALUES (?, ?, ?, ?)", (userid, 0, 0,0))

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
            i += 1
            print(i)
            # mod powerlevel
            modpl = self.getpowerlevel(ctx, dodger=modM[i-1])
            print(modpl)
            modroll = int(self.dice())
        
            print(str(modpl) + " vs " + str(dodgerpl))

            embed.add_field(name=str(i) + " of " + str(rolls), value="", inline=False)
            
            if modpl > dodgerpl:
                modroll = modroll + 2
            else:
                modroll = modroll - 1
            if modroll > dodgerac:
                hitcounter += 1
                inittitle = str(ctx.author.display_name + ' has been hit ' + str(hitcounter) + " times")
                embed = discord.Embed(color=0x9062d3, title = inittitle)
                embed.set_thumbnail(url=modM[i-1].avatar.url)
                embed.set_footer(text=str(modroll) + "/20 > " + str(dodgerac))
                embed.add_field(name=str(modM[i-1].display_name) + " shoots " + str(dodger), value=str(dodger) + " has been hit!", inline=False)
                
            else: 
                inittitle = str(ctx.author.display_name + ' has been hit ' + str(hitcounter) + " times")
                embed = discord.Embed(color=0x9062d3, title = inittitle)
                embed.set_thumbnail(url=ctx.author.avatar.url)
                embed.set_footer(text=str(modroll) + "/20 ≤ " + str(dodgerac))
                embed.add_field(name=str(modM[i-1].display_name) + " shoots " + str(dodger), value=str(dodger) + " dodges!", inline=False)

            await asyncio.sleep(3)
            await emby.edit(embed=embed)

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
    
    
