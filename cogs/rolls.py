from time import sleep
import discord
from discord import app_commands
from discord.ext import commands, tasks
import json, random
import asyncio
import aiosqlite
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import io
from io import BytesIO

gbfgid = '339155308767215618'
borpaspin = '<a:borpaspin:905835451204640829>'
goldborpaspin = '<a:goldborpaspin:906324859007696916>'
rainbowborpaspin = '<a:rainbowborpaspin:1447183660640894996>'
plusone = '<:plusone:899989682555854868>'
loading = '<a:loading:1446857889711915144>'
tick = '✅'
cross = '❌'
umproll = '<a:umproll:903953063746883614>'


channellist = [1446500430954631359]
channellist = [1446500430954631359,262371002577715201]
mainchannel = [9262371002577715201]
data =[]  

mainch = True

  



async def rolling(user):
    db = await aiosqlite.connect('rolls.db')
    theroll = random.randint(1,1000)
    if theroll <= 1:
        roll = rainbowborpaspin
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user])
        await db.execute("UPDATE rolltable SET rainbowborpaspins=rainbowborpaspins+1 WHERE user=?",[user])
        await db.commit()
        await db.close()
        return roll 
    if theroll <= 5:
        roll = goldborpaspin
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user])
        await db.execute("UPDATE rolltable SET goldborpaspins=goldborpaspins+1 WHERE user=?",[user])
        await db.commit()
        await db.close()
        return roll
    if theroll <= 60:
        roll = borpaspin
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user])
        await db.execute("UPDATE rolltable SET borpas=borpas+1 WHERE user=?",[user])
        await db.commit()
        await db.close()
        return roll
    else:
        roll = "cum"
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user])
        await db.execute("UPDATE rolltable SET cums=cums+1 WHERE user=?",[user])
        await db.commit()
        await db.close()
        return roll
    
async def dbget():
    db = await aiosqlite.connect('rolls.db')
    cursor = await db.execute('SELECT user, rolls FROM rolltable')
    rows = await cursor.fetchall()
    data = [{'user': a,'rolls': b,} for a,b in rows]
    #print("dbget - finished")
    await db.close()
    return data

class rollsCog(commands.Cog, name="rolls"):
    def __init__(self, bot):
        self.bot = bot
        self.freecummies.start()
        
    
    #DEBBUGGING STUFF

    @commands.command()
    @commands.has_role("cumdev")
    async def ct(self,ctx):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
            async with aiosqlite.connect('rolls.db') as db:
                    await db.execute("CREATE TABLE rolltable (user INT UNIQUE, alias TEXT, rolls INT, totalrolls INT, cums INT, borpas INT, goldborpaspins INT, rainbowborpaspins INT);")
                    await db.commit()
                    print("table created")
                    await ctx.message.add_reaction(tick)
        else: 
            await ctx.message.add_reaction(cross)

    @commands.command()
    @commands.has_role("cumdev")
    async def dt(self,ctx):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
            async with aiosqlite.connect('rolls.db') as db:
                await db.execute("DROP TABLE rolltable")
                await db.commit()
                await ctx.message.add_reaction(tick)
                print("table dropped")
        else: 
            await ctx.message.add_reaction(cross)

    @commands.command()
    @commands.has_role("cumdev")
    async def setroll(self,ctx, arg1, arg2):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
            async with aiosqlite.connect('rolls.db') as db:
                try:
                    await db.execute("UPDATE rolltable SET rolls=? WHERE user=?",(arg1,arg2))
                    await db.commit()
                    print("set rolls to " + arg1)
                    await ctx.message.add_reaction(tick)
                except:
                    print("something went wrong")
                    await ctx.message.add_reaction(cross)

    #USER COMMANDS
    #ROLLS

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cum(self, ctx):
        if ctx.channel.id in channellist:
            await ctx.message.add_reaction(loading) 
            data = await dbget()
            playerid = ctx.author.id
            alias = ctx.author.name
            #check if author is in db
            if any(i['user'] == playerid for i in data):
                print("player exists: " + str(playerid)) 
            else:
                #add author to db
                async with aiosqlite.connect('rolls.db') as db:
                    await db.execute("INSERT INTO rolltable VALUES (?, ?, ?, 0, 0, 0, 0);", (playerid, alias, 11))
                    await db.commit()
                    await ctx.reply("Look here everyone a new cummer!")
            #get updated db value
            data = await dbget()
            match = next((item for item in data if item['user'] == playerid), 'Nothing Found')
            if int(match['rolls']) > 0:
                async with aiosqlite.connect('rolls.db') as db:
                    await db.execute("UPDATE rolltable SET rolls=rolls-1 WHERE user=?",[playerid])
                    await db.commit()
                    roll = await rolling(playerid)
                    sent = await ctx.reply(roll)
                    await asyncio.sleep(7)
                    await sent.delete()
                    await ctx.message.remove_reaction(loading, member=self.bot.get_user(562335932813017134)) 
                    await ctx.message.add_reaction(tick)
                    await asyncio.sleep(3)
                    await ctx.message.delete()
                    
            else: 
                sent = await ctx.reply("u got no cums loser")
                await asyncio.sleep(7)
                await sent.delete()
                await ctx.message.remove_reaction(loading, member=self.bot.get_user(562335932813017134)) 
                await ctx.message.add_reaction(tick) 
                await asyncio.sleep(3)
                await ctx.message.delete()

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def cum10(self, ctx):
        if ctx.channel.id in channellist:
            await ctx.message.add_reaction(loading) 
            data = await dbget()
            playerid = ctx.author.id
            #check if author is in db
            if any(i['user'] == playerid for i in data):
                print("player exists: " + str(playerid)) 
            else:
                await ctx.reply("u got no cums loser")
                await ctx.message.remove_reaction(loading, member=self.bot.get_user(562335932813017134))
                return

            #get updated db value
            data = await dbget()
            match = next((item for item in data if item['user'] == playerid), 'Nothing Found')
            if int(match['rolls']) >= 10:
                async with aiosqlite.connect('rolls.db') as db:
                    await db.execute("UPDATE rolltable SET rolls=rolls-10 WHERE user=?",[playerid])
                    await db.commit()
                    totalrolls = []
                    embed = discord.Embed(title="Test your luck",color=0x9062d3)
                    embed.add_field(name="Rolls...", value="rolling...")
                    sent = await ctx.reply(embed=embed)
                    for i in range(10):
                        await asyncio.sleep(1)
                        roll = await rolling(playerid)
                        totalrolls.append(roll)
                        sendies = (', '.join('%s x%d' % (item, count) for item, count in sorted(Counter(totalrolls).items())))
                        embed.set_field_at(0, name="Rolls...", value=sendies, inline=True)
                        await sent.edit(embed=embed)
                    await asyncio.sleep(7)
                    await sent.delete()
                    await ctx.message.remove_reaction(loading, member=self.bot.get_user(562335932813017134)) 
                    await ctx.message.add_reaction(tick)
                    await asyncio.sleep(3)
                    await ctx.message.delete()
            else: 
                sent = await ctx.reply("u dont got enough cums loser")
                await asyncio.sleep(7)
                await sent.delete()
                await ctx.message.remove_reaction(loading, member=self.bot.get_user(562335932813017134)) 
                await ctx.message.add_reaction(tick) 
                await asyncio.sleep(3)
                await ctx.message.delete()

    @app_commands.command(name="borpacheck", description="check the top borpaspinners")
    async def borpacheck(self, interaction: discord.Interaction):
        try: 
            if interaction.channel_id not in channellist:
                await interaction.response.send_message("This command can't be used in this channel.", ephemeral=True)
                return
            db = await aiosqlite.connect('rolls.db')
            cursor = await db.execute('SELECT alias, borpas FROM rolltable ORDER BY borpas DESC LIMIT 5')
            rows = await cursor.fetchall()
            ctopid = await db.execute("SELECT user FROM rolltable ORDER BY borpas DESC LIMIT 1")
            topid = await ctopid.fetchone()
            top5 = [{'user': a,'borpas': b,} for a,b in rows]
            display = [("%s: %s borpas spun"%(item['user'],item['borpas'])) for item in top5]
            sep = '\n'
            embed = discord.Embed(title="Top Borpaspinners!",color=0x9062d3)
            top = self.bot.get_user(topid[0])
            embed.set_thumbnail(url=top.avatar.url)
            embed.add_field(name="​", value=sep.join(display), inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await db.close()

        except Exception as e:
            print("borpacheck error:", repr(e))
            try:
                await interaction.response.send_message("An internal error occurred.", ephemeral=True)
            except:
                pass

    @app_commands.command(name="goldcheck", description="check the top gold borpaspinners")
    async def goldcheck(self, interaction: discord.Interaction):
        try: 
            if interaction.channel_id not in channellist:
                await interaction.response.send_message("This command can't be used in this channel.", ephemeral=True)
                return
            db = await aiosqlite.connect('rolls.db')
            cursor = await db.execute('SELECT alias, goldborpaspins FROM rolltable ORDER BY goldborpaspins DESC LIMIT 5')
            rows = await cursor.fetchall()
            ctopid = await db.execute("SELECT user FROM rolltable ORDER BY goldborpaspins DESC LIMIT 1")
            topid = await ctopid.fetchone()
            top5 = [{'user': a,'goldborpaspins': b,} for a,b in rows]
            display = [("%s: %s gold borpas spun"%(item['user'],item['goldborpaspins'])) for item in top5]
            sep = '\n'
            embed = discord.Embed(title="Top Gold Borpa Spinners!",color=0x9062d3)
            top = self.bot.get_user(topid[0])
            embed.set_thumbnail(url=top.avatar.url)
            embed.add_field(name="​", value=sep.join(display), inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await db.close()
        
        except Exception as e:
            print("goldcheck error:", repr(e))
            try:
                await interaction.response.send_message("An internal error occurred.", ephemeral=True)
            except:
                pass
    
# 1. Decorator uses app_commands, not commands
    @app_commands.command(name="cumstats", description="check stats for yourself or another user")
    @app_commands.describe(userid="user id or blank for yourself")
    async def cumstats(self, interaction: discord.Interaction, userid: str = ""):
        try:
            if interaction.channel_id not in channellist:
                await interaction.response.send_message("This command can't be used in this channel.", ephemeral=True)
                return
            if userid and userid.isnumeric():
                playerid = int(userid)
            else:
                playerid = interaction.user.id

            db = await aiosqlite.connect('rolls.db')
            cursor = await db.execute('SELECT rolls, totalrolls, cums, borpas, goldborpaspins FROM rolltable WHERE user=?', [playerid])
            rows = await cursor.fetchall()
            await db.close()
            if not rows:
                await interaction.response.send_message("User not found in database!", ephemeral=True)
                return
            stats = [{'rolls saved': b, 'total rolls': c, 'cums': d, 'borpaspins': e, 'goldborpaspins': f} for b,c,d,e,f in rows]
            listedstats = [f"{k}: {v}" for k,v in stats[0].items()]
            final = "\n".join(listedstats)
            member = self.bot.get_user(playerid)
            if not member:
                await interaction.response.send_message("Could not find user!", ephemeral=True)
                return
            embed = discord.Embed(title=f"{member.name}'s stats", color=0x9062d3)
            embed.set_thumbnail(url=member.avatar.url)
            embed.add_field(name="​", value=final, inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            print("cumstats error:", repr(e))
            try:
                await interaction.response.send_message("An internal error occurred.", ephemeral=True)
            except:
                pass

    @commands.command()
    async def pt(self, ctx): 
        if ctx.channel.id in channellist: 
            db = await aiosqlite.connect('rolls.db')
            cursor = await db.execute('SELECT alias, rolls, totalrolls, cums, borpas, goldborpaspins FROM rolltable WHERE totalrolls>9')
            stats = await cursor.fetchall()
            await db.close()
            stats = [{'name': a, 'rolls': b, 'total rolls': c, 'cums': d, 'total borpas': e+f, 'percent': round((e+f)/c*100, 2)} for a,b,c,d,e,f in stats]
            adder = {'name': 'Likely Rate', 'rolls': '0','total rolls': 100, 'cums': 96, 'total borpas': 6, 'percent': 6}
            stats.append(adder)
            newlist = sorted(stats, key=lambda d: d['percent'])
            df = pd.DataFrame(newlist)
            fig, ax = plt.subplots()
            plt.style.use('ggplot')
            clrs = ['r' if (x == 6) else 'c' for x in df['percent']]
            plt.barh(df['name'], df['percent'], color=clrs)
            fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
            xticks = mtick.FormatStrFormatter(fmt)
            ax.xaxis.set_major_formatter(xticks)

            plt.title('Borpa rates')
            plt.ylabel('Users')
            plt.xlabel('Rates')

            with io.BytesIO() as image_binary:
                plt.savefig(image_binary)
                image_binary.seek(0)
                await ctx.channel.send(file=discord.File(fp=image_binary, filename='image.png'))


    @commands.command()
    async def pt2(self, ctx): 
        if ctx.channel.id in channellist: 
            db = await aiosqlite.connect('rolls.db')
            cursor = await db.execute('SELECT alias, rolls, totalrolls, cums, borpas, goldborpaspins FROM rolltable WHERE totalrolls>9')
            stats = await cursor.fetchall()
            await db.close()
            stats = [{'name': a, 'rolls': b, 'total rolls': c, 'cums': d, 'total borpas': e+f, 'percent': round((e+f)/c*100, 2)} for a,b,c,d,e,f in stats]
            newlist = sorted(stats, key=lambda d: d['percent'])
            df = pd.DataFrame(newlist)
            fig, ax = plt.subplots()
            plt.style.use('ggplot')
            clrs = ['c']
            ax.axhline(y=6,color='r',linestyle='-')
            ax.scatter(df['total rolls'], df['percent'], color=clrs)
            fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
            xticks = mtick.FormatStrFormatter(fmt)
            ax.yaxis.set_major_formatter(xticks)
            names = df['name'].tolist()
            xas = df['total rolls'].tolist()
            yas = df['percent'].tolist()

            for i, txt in enumerate(names):
                ax.annotate(txt, (xas[i], yas[i]))
            
            plt.title('Rates vs Total Rolls')
            plt.ylabel('Borpa Rates')
            plt.xlabel('Totall Rolls')

            with io.BytesIO() as image_binary:
                plt.savefig(image_binary)
                image_binary.seek(0)
                await ctx.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

    @app_commands.command(name="cumhelp", description="get help with cum commands")
    async def cuhelp(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Cum Help!",description="Slash Commands:\n- /cumstats\n- /borpacheck\n- /goldcheck\n\nDot Commands:\n- .cum [cooldown: 5 seconds]\n- .cum10 [cooldown: 15 seconds]",color=0x9062d3)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)






    #LISTENERS 

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.id) == '262371002577715201':
            textroll = random.randint(1,200)
            if textroll  <= 3:
                playerid = message.author.id
                playername = message.author.name
                try:
                    async with aiosqlite.connect('rolls.db') as db:
                        await db.execute("UPDATE rolltable SET rolls=rolls+1 WHERE user=?",[playerid])
                        await db.commit()
                        await message.add_reaction(plusone) 
                        channel = self.bot.get_channel(902418660767965184)
                        await channel.send(playername + " rolled: " + str(textroll))
                except:
                    print('no user')

    #LOOPS

    @tasks.loop(hours=24)
    async def freecummies(self):
        async with aiosqlite.connect('rolls.db') as db:
                await db.execute("UPDATE rolltable SET rolls=rolls+10")
                await db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        await dbget()

async def setup(bot):
    await bot.add_cog(rollsCog(bot))
    print('rolls cog loaded')

