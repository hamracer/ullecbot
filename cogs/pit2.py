import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import os
import psycopg
import psycopg_pool
from dotenv import load_dotenv
import sys



if sys.platform == 'win32':
    path=str(os.getcwd()) + '\configs\.env'
else:
    path=str(os.getcwd()) + '/configs/.env'
load_dotenv(override=True,dotenv_path=path)
connection_string = os.getenv('DATABASE_URL')
print(connection_string)
pool = psycopg_pool.AsyncConnectionPool(conninfo=connection_string, open=False)

class pit2Cog(commands.Cog, name="pit2"):

    def __init__(self, bot):
        self.bot = bot

    # for rolling a d20, returns value
    def dice(self):
        diceroll = random.randint(1,20)
        return diceroll

    # for account age, returns account age in months
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
        
    # for testing the DB connection, prints time + version
    async def testdb(self):
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
        return

    # for creating the table
    @commands.command()
    @commands.has_role("cumdev")
    async def ct(self, ctx):
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("CREATE TABLE pit2 (userid bigint PRIMARY KEY, kills integer, clears integer, deaths integer)")
                print("table created")

    @commands.command()
    @commands.has_role("cumdev")
    async def setupdb(self, ctx):
        print('setup')
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                modrole = discord.utils.get(ctx.guild.roles, name="mod")
                modnum = [m.name for m in modrole.members]
                modlen = len(modnum)
                modM = [m for m in modrole.members]
                i = 0
                while modlen > i:
                    print(i)
                    i += 1
                    modid = modM[i-1].id
                    print(modid)
                    try: 
                        await cur.execute("INSERT INTO pit2 (userid, kills, clears, deaths) VALUES (%s, %s, %s, %s)", (modid, 0, 0, 0))
                        print('added mod')
                    except:
                        print('user already exists')
                print("setup for mod role")



    # calls the testdb function
    @commands.command()
    @commands.has_role("cumdev")
    async def test(self, ctx):
        await pool.open()
        await self.testdb()


    @commands.command()
    async def bh(self, ctx):
        await pool.open()
        print('bullethell')
        dodger = ctx.author
        userid = ctx.author.id
        dodgerpl = self.getpowerlevel(ctx, dodger)
        #id check
        print('starting id check')
        inittitle = str(ctx.author.display_name + ' runs the gauntlet')
        embed = discord.Embed(color=0x9062d3, title = inittitle)
        async with pool.connection() as conn:
            print('pool connection')
            async with conn.cursor() as cur:
                print('cursor connection')
                try:
                    print('does the user exists')
                    await cur.execute("SELECT * FROM pit2 WHERE userid=%s",(userid,))
                    checky = await cur.fetchone()
                    print(userid)
                    print(checky[0])
                    userid == checky[0]
                    print(checky[2])
                    if checky[2] == 0:
                        embed.add_field(name=ctx.author.display_name + " has not previously escaped", value="", inline=False)
                    print("1")
                    if checky[2] == 1:
                        embed.add_field(name=ctx.author.display_name + " has previously escaped " + str(checky[2]) + " time", value="", inline=False)
                    print("2")
                    if checky[2] >= 2:
                        print("3")
                        embed.add_field(name=ctx.author.display_name + " has previously escaped " + str(checky[2]) + " times", value="", inline=False)
                    
                except:
                    print('fails to find')
                    await cur.execute("INSERT INTO pit2 (userid, kills, clears, deaths) VALUES (%s, %s, %s, %s)", (userid, 0, 0, 0,))
                    print('user created')

        modrole = discord.utils.get(ctx.guild.roles, name="mod")
        modnum = [m.name for m in modrole.members]
        
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
                modroll = modroll + 1
            else:
                modroll = modroll - 1
            if modroll > dodgerac:
                print('hit')
                hitcounter += 1
                inittitle = str(ctx.author.display_name + ' has been hit ' + str(hitcounter) + " times")
                embed = discord.Embed(color=0x9062d3, title = inittitle)
                embed.set_thumbnail(url=modM[i-1].avatar.url)
                embed.set_footer(text=str(modroll) + "/20 > " + str(dodgerac))
                embed.add_field(name=str(modM[i-1].display_name) + " shoots " + str(dodger), value=str(dodger) + " has been hit!", inline=False)
                async with pool.connection() as conn:
                    async with conn.cursor() as cur:
                        modid = modM[i-1].id
                        await cur.execute("UPDATE pit2 SET kills=kills+1 WHERE userid=%s",(modid,))
                        print('added kill')
                
            else: 
                print('dodge')
                inittitle = str(ctx.author.display_name + ' has been hit ' + str(hitcounter) + " times")
                embed = discord.Embed(color=0x9062d3, title = inittitle)
                embed.set_thumbnail(url=ctx.author.avatar.url)
                embed.set_footer(text=str(modroll) + "/20 ≤ " + str(dodgerac))
                embed.add_field(name=str(modM[i-1].display_name) + " shoots " + str(dodger), value=str(dodger) + " dodges!", inline=False)

            await asyncio.sleep(2)
            await emby.edit(embed=embed)

        await asyncio.sleep(3)
        if hitcounter > 0:
            print('death!')
            pittimer = pow(2,int(hitcounter))
            inittitle = str(ctx.author.display_name + ' has been pitted for ' + str(pittimer) + " minutes")
            embed = discord.Embed(color=0x9062d3, title = inittitle)
            embed.set_thumbnail(url=ctx.author.avatar.url)
            embed.set_footer(text="2^" + str(hitcounter))
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("UPDATE pit2 SET deaths=deaths+1 WHERE userid=%s",(dodger.id,))
                    try:
                        await dodger.timeout(timedelta(minutes=float(pittimer)))
                        await cur.execute("SELECT * FROM pit2 ORDER BY kills DESC")
                        stat = await cur.fetchone()
                        topshooter = await (ctx.bot.fetch_user(stat[0]))
                        embed.add_field(name=topshooter.display_name + " is the top active shooter with " + str(stat[1]) + " kills", value="", inline=False)
                        embed.add_field(name=ctx.author.display_name + " has been pitted " + str(stat[3]) + " times", value="", inline=False)
                    except:
                        embed.add_field(name="this guy is too powerful to pit", value="", inline=False)
                    
            await emby.edit(embed=embed)


            
        
        else:
            print('clear')
            inittitle = str(ctx.author.display_name + ' has escaped the pit!')
            embed = discord.Embed(color=0x9062d3, title = inittitle)
            embed.set_thumbnail(url=ctx.author.avatar.url)
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("UPDATE pit2 SET clears=clears+1 WHERE userid=%s",(dodger.id,))
                    print('added clear')
                    await cur.execute("SELECT * FROM pit2 WHERE userid=%s",(userid,))
                    poop = await cur.fetchone()
                    
            embed.set_footer(text=ctx.author.display_name + " has escaped the pit " + str(poop[2]) + " times")
            await emby.edit(embed=embed)




async def setup(bot):
    await bot.add_cog(pit2Cog(bot))
    print('pit2 cog loaded')
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) 
    
    
    
