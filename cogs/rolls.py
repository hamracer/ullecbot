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
channellist = [1446500430954631359,1447552037100453909]
mainchannel = [9262371002577715201]
data =[]  

mainch = True

  



async def rolling(user_id, multiplier=1):
    db = await aiosqlite.connect('rolls.db')
    cursor = await db.execute("SELECT boss_kills FROM rolltable WHERE user=?", [user_id])
    result = await cursor.fetchone()
    boss_kills = result[0] if result and result[0] is not None else 0

    # 0.1% bonus per kill, so 0.001
    bonus_chance = boss_kills

    theroll = random.randint(1,1000)
    if theroll <= (1 * multiplier) + bonus_chance:
        roll = rainbowborpaspin
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user_id])
        await db.execute("UPDATE rolltable SET rainbowborpaspins=rainbowborpaspins+1 WHERE user=?",[user_id])
        await db.commit()
        await db.close()
        return roll 
    if theroll <= (5 * multiplier) + bonus_chance:
        roll = goldborpaspin
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user_id])
        await db.execute("UPDATE rolltable SET goldborpaspins=goldborpaspins+1 WHERE user=?",[user_id])
        await db.commit()
        await db.close()
        return roll
    if theroll <= (60 * multiplier) + bonus_chance:
        roll = borpaspin
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user_id])
        await db.execute("UPDATE rolltable SET borpas=borpas+1 WHERE user=?",[user_id])
        await db.commit()
        await db.close()
        return roll
    else:
        roll = "cum"
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user_id])
        await db.execute("UPDATE rolltable SET cums=cums+1 WHERE user=?",[user_id])
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
        self.boss_regen.start()
        
    
    #DEBBUGGING STUFF

    @commands.command()
    @commands.has_role("cumdev")
    async def ct(self,ctx):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
            async with aiosqlite.connect('rolls.db') as db:
                    await db.execute("CREATE TABLE rolltable (user INT UNIQUE, alias TEXT, rolls INT, totalrolls INT, cums INT, borpas INT, goldborpaspins INT, rainbowborpaspins INT, boss_kills INT);")
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
                    await db.execute("INSERT INTO rolltable VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0);", (playerid, alias, 110))
                    await db.commit()
                    await ctx.reply("Look here everyone a new cummer!")
            #get updated db value
            data = await dbget()
            match = next((item for item in data if item['user'] == playerid), 'Nothing Found')
            if int(match['rolls']) > 0:
                async with aiosqlite.connect('rolls.db') as db:
                    await db.execute("UPDATE rolltable SET rolls=rolls-1 WHERE user=?",[playerid])
                    await db.commit()
                    roll = await rolling(playerid, multiplier=1)
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
    @commands.cooldown(2, 15, commands.BucketType.guild)
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
                        roll = await rolling(playerid, multiplier=1)
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

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def bigcum(self, ctx):
        """Rolls 100 times, but you have to win a coin flip first!"""
        if ctx.channel.id not in channellist:
            return

        await ctx.message.add_reaction(loading)
        data = await dbget()
        playerid = ctx.author.id
        alias = ctx.author.name

        # Check if author is in db
        if not any(i['user'] == playerid for i in data):
            await ctx.reply("u got no cums loser, use .cum first")
            await ctx.message.remove_reaction(loading, self.bot.user)
            return

        # Get updated db value and check rolls
        data = await dbget()
        match = next((item for item in data if item['user'] == playerid), None)
        if not match or int(match['rolls']) < 100:
            sent = await ctx.reply("u dont got enough cums for this (100 required)")
            await ctx.message.remove_reaction(loading, self.bot.user)
            await asyncio.sleep(7)
            await sent.delete()
            await ctx.message.delete()
            return

        # --- Coin Flip ---
        flip_msg = await ctx.reply("This is a big one. You're betting 100 rolls. Call it in the air. `heads` or `tails`? (15s to answer)")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['heads', 'tails']

        try:
            choice_msg = await self.bot.wait_for('message', check=check, timeout=15.0)
            user_choice = choice_msg.content.lower()
            try:
                await choice_msg.delete()
            except discord.Forbidden:
                pass  # Can't delete messages, oh well
        except asyncio.TimeoutError:
            await flip_msg.edit(content="Too slow! The chance is gone. No cums lost.")
            await ctx.message.remove_reaction(loading, self.bot.user)
            await asyncio.sleep(7)
            await flip_msg.delete()
            await ctx.message.delete()
            return

        # User made a choice, so they are committed. Subtract rolls.
        async with aiosqlite.connect('rolls.db') as db:
            await db.execute("UPDATE rolltable SET rolls=rolls-100 WHERE user=?", [playerid])
            await db.commit()

        coin_result = random.choice(['heads', 'tails'])

        if user_choice != coin_result:
            # --- Lose the flip ---
            await flip_msg.edit(content=f"It was **{coin_result}**. You lose your 100 cum bet. L")
            
            # Simulate what they would have won
            async with aiosqlite.connect('rolls.db') as db:
                cursor = await db.execute("SELECT boss_kills FROM rolltable WHERE user=?", [playerid])
                result = await cursor.fetchone()
                boss_kills = result[0] if result and result[0] is not None else 0
            
            bonus_chance = boss_kills
            lost_rolls = []
            for _ in range(100):
                theroll = random.randint(1,1000)
                if theroll <= 2 + bonus_chance:
                    lost_rolls.append(rainbowborpaspin)
                elif theroll <= 10 + bonus_chance:
                    lost_rolls.append(goldborpaspin)
                elif theroll <= 120 + bonus_chance:
                    lost_rolls.append(borpaspin)
                else:
                    lost_rolls.append("cum")
            
            sendies = (', '.join('%s x%d' % (item, count) for item, count in sorted(Counter(lost_rolls).items())))
            embed = discord.Embed(title="BIG CUM (LOST)", color=0xff0000, description=f"for {alias}")
            embed.add_field(name="You would have won...", value=sendies, inline=False)
            lost_msg = await ctx.send(embed=embed)

            await ctx.message.remove_reaction(loading, self.bot.user)
            await ctx.message.add_reaction(cross)
            await asyncio.sleep(10)
            await flip_msg.delete()
            await lost_msg.delete()
            await ctx.message.delete()
            return

        # --- Win the flip ---
        await flip_msg.edit(content=f"You called it! It was **{coin_result}**. Here we go!")

        totalrolls_list = []
        embed = discord.Embed(title="BIG CUM", color=0x9062d3, description=f"for {alias}")
        embed.add_field(name="Rolls... (0/100)", value="rolling...")
        roll_msg = await ctx.send(embed=embed)

        for i in range(10):  # 10 batches
            for _ in range(10):  # 10 rolls per batch
                roll = await rolling(playerid, multiplier=2)
                totalrolls_list.append(roll)

            sendies = (', '.join('%s x%d' % (item, count) for item, count in sorted(Counter(totalrolls_list).items())))
            embed.set_field_at(0, name=f"Rolls... ({len(totalrolls_list)}/100)", value=sendies, inline=False)
            await roll_msg.edit(embed=embed)
            if i < 9:  # Don't sleep on the last iteration
                await asyncio.sleep(1.5)

        # Check for triple borpa bonus
        counts = Counter(totalrolls_list)
        if counts[borpaspin] > 0 and counts[goldborpaspin] > 0 and counts[rainbowborpaspin] > 0:
            borpa_count = counts[borpaspin]
            gold_count = counts[goldborpaspin]
            
            async with aiosqlite.connect('rolls.db') as db:
                await db.execute("UPDATE rolltable SET borpas=borpas-?, goldborpaspins=goldborpaspins-?, rainbowborpaspins=rainbowborpaspins+? WHERE user=?", (borpa_count, gold_count, borpa_count + gold_count, playerid))
                await db.commit()
            
            # Update list for display
            totalrolls_list = [rainbowborpaspin if x in (borpaspin, goldborpaspin) else x for x in totalrolls_list]
            
            sendies = (', '.join('%s x%d' % (item, count) for item, count in sorted(Counter(totalrolls_list).items())))
            embed.set_field_at(0, name=f"Rolls... ({len(totalrolls_list)}/100) - TRIPLE BORPA BONUS!", value=sendies, inline=False)
            await roll_msg.edit(embed=embed)
            await ctx.send(f"**TRIPLE BORPA!** All borpas converted to {rainbowborpaspin}!")

        # --- Cleanup ---
        await ctx.message.remove_reaction(loading, self.bot.user)
        await ctx.message.add_reaction(tick)
        await asyncio.sleep(15)  # a bit longer to see results

        await roll_msg.delete()
        await flip_msg.delete()
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
                try:
                    playerid = int(userid)
                except ValueError:
                    await interaction.response.send_message("Invalid user ID provided.", ephemeral=True)
                    return
            else:
                playerid = interaction.user.id

            db = await aiosqlite.connect('rolls.db')
            # Fetch stats from rolltable
            roll_cursor = await db.execute('SELECT rolls, totalrolls, cums, borpas, goldborpaspins, rainbowborpaspins, boss_kills FROM rolltable WHERE user=?', [playerid])
            roll_stats = await roll_cursor.fetchone()

            if not roll_stats:
                await db.close()
                await interaction.response.send_message("User not found in database!", ephemeral=True)
                return

            # Fetch total damage from boss_damage table
            damage_cursor = await db.execute('SELECT SUM(damage) FROM boss_damage WHERE user=?', [playerid])
            total_damage_stat = await damage_cursor.fetchone()
            total_damage = total_damage_stat[0] if total_damage_stat and total_damage_stat[0] is not None else 0
            await db.close()

            stats_dict = {
                'rolls saved': roll_stats[0], 'total rolls': roll_stats[1], 'cums': roll_stats[2], 
                'borpaspins': roll_stats[3], 'goldborpaspins': roll_stats[4], 'rainbowborpaspins': roll_stats[5],
                'boss_kills': roll_stats[6], 'total_damage_done': f"{total_damage:,}"
            }
            
            total_borpas = roll_stats[3] + roll_stats[4] + roll_stats[5]
            stats_dict['damage_per_borpa'] = f"{total_damage / total_borpas:,.2f}" if total_borpas > 0 else "0.00"

            member = self.bot.get_user(playerid)
            listedstats = [f"**{k.replace('_', ' ').title()}**: {v}" for k,v in stats_dict.items()]
            final = "\n".join(listedstats)
            embed = discord.Embed(title=f"{member.name}'s stats", color=0x9062d3)
            embed.set_thumbnail(url=member.display_avatar.url)
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
            # Get rolls data
            cursor = await db.execute('SELECT user, alias, rolls, totalrolls, cums, borpas, goldborpaspins, rainbowborpaspins FROM rolltable WHERE totalrolls>9')
            stats = await cursor.fetchall()

            # Get spent borpas from boss_damage table
            spent_cursor = await db.execute("SELECT user, roll_type FROM boss_damage WHERE roll_type IN ('borpaspin', 'gold', 'rainbow')")
            spent_data = await spent_cursor.fetchall()
            await db.close()

            # Count spent borpas per user
            spent_counts = Counter(row[0] for row in spent_data if row[1] in ('borpaspin', 'gold', 'rainbow'))

            processed_stats = []
            for user_id, alias, rolls, totalrolls, cums, borpas, goldborpaspins, rainbowborpaspins in stats:
                borpas_earned = borpas + goldborpaspins + rainbowborpaspins
                borpas_spent = spent_counts.get(user_id, 0)
                total_borpas_obtained = borpas_earned + borpas_spent
                percent = round((total_borpas_obtained / totalrolls) * 100, 2) if totalrolls > 0 else 0
                processed_stats.append({'name': alias, 'rolls': rolls, 'total rolls': totalrolls, 'cums': cums, 'total borpas': total_borpas_obtained, 'rainbow borpas': rainbowborpaspins, 'percent': percent})

            adder = {'name': 'Likely Rate', 'rolls': '0','total rolls': 100, 'cums': 96, 'total borpas': 6, 'rainbow borpas': 0, 'percent': 6}
            processed_stats.append(adder)
            newlist = sorted(processed_stats, key=lambda d: d['percent'])
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
            # Get rolls data
            cursor = await db.execute('SELECT user, alias, rolls, totalrolls, cums, borpas, goldborpaspins, rainbowborpaspins FROM rolltable WHERE totalrolls>9')
            stats = await cursor.fetchall()

            # Get spent borpas from boss_damage table
            spent_cursor = await db.execute("SELECT user, roll_type FROM boss_damage WHERE roll_type IN ('borpaspin', 'gold', 'rainbow')")
            spent_data = await spent_cursor.fetchall()
            await db.close()

            # Count spent borpas per user
            spent_counts = Counter(row[0] for row in spent_data if row[1] in ('borpaspin', 'gold', 'rainbow'))

            processed_stats = []
            for user_id, alias, rolls, totalrolls, cums, borpas, goldborpaspins, rainbowborpaspins in stats:
                borpas_earned = borpas + goldborpaspins + rainbowborpaspins
                borpas_spent = spent_counts.get(user_id, 0)
                total_borpas_obtained = borpas_earned + borpas_spent
                percent = round((total_borpas_obtained / totalrolls) * 100, 2) if totalrolls > 0 else 0
                processed_stats.append({'name': alias, 'rolls': rolls, 'total rolls': totalrolls, 'cums': cums, 'total borpas': total_borpas_obtained, 'rainbow borpas': rainbowborpaspins, 'percent': percent})
            df = pd.DataFrame(processed_stats)
            # Increase figure size for better readability
            fig, ax = plt.subplots(figsize=(16, 10))
            plt.style.use('ggplot')
            clrs = ['c']
            
            # Add a horizontal line for the expected rate and a grid for clarity
            ax.axhline(y=6,color='r',linestyle='-')
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            ax.scatter(df['total rolls'], df['percent'], color=clrs)
            
            fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
            yticks = mtick.FormatStrFormatter(fmt)
            ax.yaxis.set_major_formatter(yticks)
            
            names = df['name'].tolist()
            xas = df['total rolls'].tolist()
            yas = df['percent'].tolist()

            for i, txt in enumerate(names):
                # Annotate with a slight offset and smaller font to improve readability
                ax.annotate(txt, (xas[i], yas[i]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)
            
            plt.title('Rates vs Total Rolls')
            plt.ylabel('Borpa Rates')
            plt.xlabel('Total Rolls')
            plt.tight_layout() # Adjust layout to prevent labels from being cut off
            
            with io.BytesIO() as image_binary:
                plt.savefig(image_binary)
                image_binary.seek(0)
                await ctx.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

    @commands.command()
    async def dpb(self, ctx):
        if ctx.channel.id in channellist:
            await ctx.message.add_reaction(loading)
            db = await aiosqlite.connect('rolls.db')

            # Get all user stats from rolltable
            cursor = await db.execute('SELECT user, alias, borpas, goldborpaspins, rainbowborpaspins FROM rolltable')
            stats = await cursor.fetchall()

            # Get total damage and spent borpas for all users
            damage_cursor = await db.execute("SELECT user, SUM(damage), roll_type FROM boss_damage GROUP BY user, roll_type")
            damage_data = await damage_cursor.fetchall()
            await db.close()

            # Process damage and spent borpas
            user_damage = Counter()
            spent_borpas = Counter()
            for user_id, damage, roll_type in damage_data:
                user_damage[user_id] += damage
                if roll_type in ('borpaspin', 'gold', 'rainbow'):
                    spent_borpas[user_id] += 1

            processed_stats = []
            for user_id, alias, borpas, goldborpaspins, rainbowborpaspins in stats:
                # Calculate total borpas (unspent + spent)
                unspent = borpas + goldborpaspins + rainbowborpaspins
                spent = spent_borpas.get(user_id, 0)
                total_borpas = unspent + spent
                
                total_damage = user_damage.get(user_id, 0)

                # Calculate damage per borpa
                dpb = (total_damage / total_borpas) if total_borpas > 0 else 0
                if dpb > 0: # Only include users with a DPB greater than 0
                    processed_stats.append({'name': alias, 'dpb': dpb})

            if not processed_stats:
                await ctx.reply("No users with damage per borpa to display.")
                await ctx.message.remove_reaction(loading, member=self.bot.user)
                return

            # Create and sort DataFrame
            df = pd.DataFrame(processed_stats).sort_values(by='dpb', ascending=True)

            # Generate Plot
            fig, ax = plt.subplots(figsize=(12, 8))
            plt.style.use('ggplot')
            ax.barh(df['name'], df['dpb'], color='skyblue')
            ax.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
            plt.title('Damage Per Borpa (DPB) Ranking')
            plt.xlabel('Damage Per Borpa')
            plt.ylabel('Users')
            plt.tight_layout()

            with io.BytesIO() as image_binary:
                plt.savefig(image_binary)
                image_binary.seek(0)
                await ctx.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
            
            await ctx.message.remove_reaction(loading, member=self.bot.user)

    @commands.command()
    async def top3(self, ctx):
        if ctx.channel.id in channellist:
            await ctx.message.add_reaction(loading)
            db = await aiosqlite.connect('rolls.db')

            # Query to get top 3 users by total damage
            cursor = await db.execute("""
                SELECT
                    t2.alias,
                    SUM(t1.damage) AS total_damage
                FROM
                    boss_damage AS t1
                JOIN
                    rolltable AS t2 ON t1.user = t2.user
                GROUP BY
                    t1.user
                ORDER BY
                    total_damage DESC
                LIMIT 3
            """)
            top_damage_data = await cursor.fetchall()
            await db.close()

            if not top_damage_data:
                await ctx.reply("No damage data available to display.")
                await ctx.message.remove_reaction(loading, member=self.bot.user)
                return

            df = pd.DataFrame(top_damage_data, columns=['name', 'total_damage']).sort_values(by='total_damage', ascending=True)

            fig, ax = plt.subplots(figsize=(10, 6))
            plt.style.use('ggplot')
            ax.barh(df['name'], df['total_damage'], color='lightcoral')
            ax.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
            plt.title('Top 3 Damage Dealers')
            plt.xlabel('Total Damage Done')
            plt.tight_layout()

            with io.BytesIO() as image_binary:
                plt.savefig(image_binary)
                image_binary.seek(0)
                await ctx.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

            await ctx.message.remove_reaction(loading, member=self.bot.user)

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
                        await db.execute("UPDATE rolltable SET rolls=rolls+10 WHERE user=?",[playerid])
                        await db.commit()
                        await message.add_reaction(plusone) 
                        channel = self.bot.get_channel(902418660767965184)
                        await channel.send(playername + " rolled: " + str(textroll))
                except:
                    print('no user')

    #LOOPS

    @tasks.loop(hours=3)
    async def freecummies(self):
        async with aiosqlite.connect('rolls.db') as db:
                await db.execute("UPDATE rolltable SET rolls=rolls+10")
                await db.commit()

    @tasks.loop(hours=1)
    async def boss_regen(self):
        """A tasks loop to regenerate the boss HP by 5% of max every hour."""
        await self.bot.wait_until_ready() # Wait for the bot to be online
        
        bosses = [
            {'path': 'configs/mpreg_hp.json', 'default_max': 100000},
            {'path': 'configs/gigampreg_hp.json', 'default_max': 500000}
        ]

        for boss in bosses:
            path = boss['path']
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                print(f"boss_regen: {path} not found or is invalid. Skipping regen.")
                continue

            current_hp = data.get('hp', 0)
            max_hp = data.get('max_hp', boss['default_max'])

            if current_hp >= max_hp:
                continue

            regen_amount = int(max_hp * 0.05)
            new_hp = min(current_hp + regen_amount, max_hp)
            data['hp'] = new_hp

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print(f"boss_regen: Boss at {path} regenerated {regen_amount} HP. New HP: {new_hp}/{max_hp}")

    @commands.Cog.listener()
    async def on_ready(self):
        await dbget()

async def setup(bot):
    await bot.add_cog(rollsCog(bot))
    print('rolls cog loaded')
