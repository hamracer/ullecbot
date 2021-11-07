from time import sleep
import discord
from discord.ext import commands, tasks
import json, random
import asyncio
import aiosqlite
from collections import Counter

gbfgid = '339155308767215618'
borpaspin = '<a:borpaspin:905835451204640829>'
goldborpaspin = '<a:goldborpaspin:906324859007696916>'
plusone = '<:plusone:899989682555854868>'
loading = '<a:loading:902407104499974144>'
tick = '<:tick:902416135683702794>'
umproll = '<a:umproll:903953063746883614>'
channellist = [262371002577715201, 853625002779869204, 562352225423458326]
mainchannel = [9262371002577715201]
data =[]  

mainch = True

  

class CustomCooldown:
    def __init__(self, rate, per, alter_rate, alter_per, bucket, *, elements):

        #def shared_cooldown(rate, per, type=commands.BucketType.default):
        #    cooldown = commands.Cooldown(rate, per, type=type)
        #    def decorator(func):
        #        if isinstance(func, discord.ext.commands.Command):
        #            func._buckets = commands.CooldownMapping(cooldown)
        #        else:
        #            func.__commands_cooldown__ = cooldown
        #        return func
        #    return decorator    

        self.elements = elements
        # Default mapping is the default cooldown
        self.default_mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)
        # Alter mapping is the alternative cooldown
        self.alter_mapping = commands.CooldownMapping.from_cooldown(alter_rate, alter_per, bucket)
        # Copy of the original BucketType
        self._bucket_type = bucket

    def __call__(self, ctx):
        key = self.alter_mapping._bucket_key(ctx.message)

        if self._bucket_type is commands.BucketType.member: # `BucketType.member` returns a tuple
            key = key[1] # The second (last) value is the member ID, the first one is the guild ID

        if key in self.elements:
            # If the key is in the elements, the bucket will be taken from the alternative cooldown
            bucket = self.alter_mapping.get_bucket(ctx.message)
        else:
            # If not, from the default cooldown
            bucket = self.default_mapping.get_bucket(ctx.message)

        # Getting the ratelimit left (can be None)
        retry_after = bucket.update_rate_limit()

        if retry_after: # If the command is on cooldown, raising the error
            raise commands.CommandOnCooldown(bucket, retry_after)
        return True

    


async def rolling(user):
    db = await aiosqlite.connect('rolls.db')
    theroll = random.randint(1,200)
    if theroll >199:
        roll = goldborpaspin
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user])
        await db.execute("UPDATE rolltable SET goldborpaspins=goldborpaspins+1 WHERE user=?",[user])
        await db.commit()
        return roll
    if theroll >= 188:
        roll = borpaspin
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user])
        await db.execute("UPDATE rolltable SET borpas=borpas+1 WHERE user=?",[user])
        await db.commit()
        return roll
    else:
        roll = "cum"
        await db.execute("UPDATE rolltable SET totalrolls=totalrolls+1 WHERE user=?",[user])
        await db.execute("UPDATE rolltable SET cums=cums+1 WHERE user=?",[user])
        await db.commit()
        return roll
    
async def dbget():
    db = await aiosqlite.connect('rolls.db')
    cursor = await db.execute('SELECT user, rolls FROM rolltable')
    rows = await cursor.fetchall()
    data = [{'user': a,'rolls': b,} for a,b in rows]
    #print("dbget - finished")
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
                    await db.execute("CREATE TABLE rolltable (user INT UNIQUE, alias TEXT, rolls INT, totalrolls INT, cums INT, borpas INT, goldborpaspins INT)")
                    await db.commit()
                    print("table created")

    @commands.command()
    @commands.has_role("cumdev")
    async def dt(self,ctx):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
            async with aiosqlite.connect('rolls.db') as db:
                await db.execute("DROP TABLE rolltable")
                await db.commit()
                print("table dropped")

    @commands.command()
    @commands.has_role("cumdev")
    async def setroll(self,ctx, arg1, arg2):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
            async with aiosqlite.connect('rolls.db') as db:
                try:
                    await db.execute("UPDATE rolltable SET rolls=? WHERE user=?",(arg1,arg2))
                    await db.commit()
                    print("set rolls to " + arg1)
                except:
                    print("something went wrong")

    #USER COMMANDS
    #ROLLS

    @commands.command()
    @commands.check(CustomCooldown(2, 60, 1, 0, commands.BucketType.channel, elements=[853625002779869204]))
    async def cum(self, ctx):
        if ctx.channel.id in channellist:
            await ctx.message.add_reaction(emoji=loading) 
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
                    await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                    await ctx.message.add_reaction(emoji=tick) 
                    
            else: 
                sent = await ctx.reply("u got no cums loser")
                await asyncio.sleep(7)
                await sent.delete()
                await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                await ctx.message.add_reaction(emoji=tick) 
                
    


    @commands.command()
    @commands.check(CustomCooldown(2, 60, 1, 0, commands.BucketType.channel, elements=[853625002779869204]))
    async def cum10(self, ctx):
        if ctx.channel.id in channellist:
            await ctx.message.add_reaction(emoji=loading) 
            data = await dbget()
            playerid = ctx.author.id
            #check if author is in db
            if any(i['user'] == playerid for i in data):
                print("player exists: " + str(playerid)) 
            else:
                await ctx.reply("u got no cums loser")
                await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134))
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
                    await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                    await ctx.message.add_reaction(emoji=tick) 
            else: 
                sent = await ctx.reply("u dont got enough cums loser")
                await asyncio.sleep(7)
                await sent.delete()
                await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                await ctx.message.add_reaction(emoji=tick) 

    @commands.command()
    @commands.check(CustomCooldown(2, 60, 1, 0, commands.BucketType.channel, elements=[853625002779869204]))
    async def howmanycumsdoihaveleft(self, ctx):
        if ctx.channel.id in channellist:
            await ctx.message.add_reaction(emoji=loading) 
            playerid = ctx.author.id
            data = await dbget()
            try:
                match = next((item for item in data if item['user'] == playerid), 'Nothing Found') 
                sent = await ctx.reply("You have " + str(match['rolls']) + " cums left.")
                await asyncio.sleep(7)
                await sent.delete()
                await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                await ctx.message.add_reaction(emoji=tick) 
            except:
                sent = await ctx.reply("You're not on the cummies list, please cum once first.")
                await asyncio.sleep(7)
                await sent.delete()
                await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                await ctx.message.add_reaction(emoji=tick) 

    
    #@commands.command()
    #async def donate(self, ctx, arg1, arg2):
    #    data = await dbget()

    #GAMES

    @commands.command()
    @commands.check(CustomCooldown(2, 60, 1, 0, commands.BucketType.channel, elements=[853625002779869204]))
    async def dice(self, ctx, arg):
        if ctx.channel.id in channellist:
            try:
                data = await dbget()
                await ctx.message.add_reaction(emoji=loading) 
                #try:
                playerid = ctx.author.id
                playername = ctx.author.name
                match = next((item for item in data if item['user'] == playerid), 'Nothing Found')
                if int(match['rolls']) >= int(arg):
                    #gamba
                    db = await aiosqlite.connect('rolls.db')
                    await db.execute("UPDATE rolltable SET rolls=rolls-? WHERE user=?",(arg,playerid))
                    await db.commit()
                    embed = discord.Embed(title="Roll the dice!",color=0x9062d3)
                    embed.add_field(name="Ullecbot", value="rolling...", inline=True)
                    embed.add_field(name=playername, value="rolling...", inline=True)
                    sent = await ctx.reply(embed=embed)

                    playerrolls=[]
                    botrolls=[]
                    for i in range(3):
                        await asyncio.sleep(1)
                        x = random.randint(1,6)
                        y = random.randint(1,6)
                        botrolls.append(x)
                        playerrolls.append(y)
                        displaybot = ', '.join(map(str,botrolls))
                        displayplayer = ', '.join(map(str,playerrolls))
                        embed.set_field_at(0, name="Ullecbot", value=displaybot, inline=True)
                        embed.set_field_at(1, name=playername, value=displayplayer, inline=True)
                        await sent.edit(embed=embed)
                    botsum = sum(botrolls)
                    playersum = sum(playerrolls)
                    if botsum > playersum:
                        resultstring = "You lose !! ( " + str(botsum) + " > " +str(playersum) + " )"
                        embed.add_field(name=resultstring, value="You lost "+ arg +" rolls", inline=False)
                    if playersum > botsum:
                        resultstring = "You win!! ( " + str(botsum) + " < " +str(playersum) + " )"
                        embed.add_field(name=resultstring, value="You win "+ arg +" rolls", inline=False)
                        arg = int(arg) + int(arg)
                        await db.execute("UPDATE rolltable SET rolls=rolls+? WHERE user=?",(arg,playerid))
                    if botsum == playersum:
                        resultstring = "You win!! ( " + str(botsum) + " = " +str(playersum) + " )"
                        embed.add_field(name=resultstring, value="Your rolls have been returned", inline=False)
                        await db.execute("UPDATE rolltable SET rolls=rolls+? WHERE user=?",(arg,playerid))
                    await db.commit()
                    await sent.edit(embed=embed)
                    await asyncio.sleep(7)
                    await sent.delete()
                    await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                    await ctx.message.add_reaction(emoji=tick) 
                    
                else:
                    await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                    await ctx.reply("You dont have enough rolls for this.")
                    await ctx.message.add_reaction(emoji=tick) 
            except:
                    sent = await ctx.reply("You dont have enough rolls for this.")
                    await asyncio.sleep(7)
                    await sent.delete()
                    await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                    await ctx.message.add_reaction(emoji=tick) 
            #except:
            #    print("something went wrong")


    #STATS

    @commands.command()
    @commands.check(CustomCooldown(2, 60, 1, 0, commands.BucketType.channel, elements=[853625002779869204]))
    async def cumsavers(self, ctx):
        if ctx.channel.id in channellist:
            await ctx.message.add_reaction(emoji=loading) 
            db = await aiosqlite.connect('rolls.db')
            cursor = await db.execute('SELECT alias, rolls FROM rolltable ORDER BY rolls DESC LIMIT 5')
            rows = await cursor.fetchall()
            ctopid = await db.execute("SELECT user FROM rolltable ORDER BY rolls DESC LIMIT 1")
            topid = await ctopid.fetchone()
            top5 = [{'user': a,'rolls': b,} for a,b in rows]
            display = [("%s: %s cums saved"%(item['user'],item['rolls'])) for item in top5]
            sep = '\n'
            embed = discord.Embed(title="Top Cum Savers!",color=0x9062d3)
            top = self.bot.get_user(topid[0])
            embed.set_thumbnail(url=top.avatar_url)
            sent = embed.add_field(name="​", value=sep.join(display), inline=False)
            await ctx.send(embed=embed)
            await asyncio.sleep(7)
            await sent.delete()
            await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
            await ctx.message.add_reaction(emoji=tick) 

    @commands.command()
    @commands.check(CustomCooldown(2, 60, 1, 0, commands.BucketType.channel, elements=[853625002779869204]))
    async def cumstats(self, ctx):
        if ctx.channel.id in channellist:
            await ctx.message.add_reaction(emoji=loading) 
            db = await aiosqlite.connect('rolls.db')
            playerid = ctx.author.id
            cursor = await db.execute('SELECT rolls, totalrolls, cums, borpas, goldborpaspins FROM rolltable WHERE user=?',[playerid])
            stats = await cursor.fetchall()
            stats = [{'rolls saved': b, 'total rolls': c, 'cums': d, 'borpaspins': e, 'goldborpaspins': f,} for b,c,d,e,f in stats]
            listedstats =[]
            for i,o in stats[0].items():
                line = i + ': ' + str(o)
                listedstats.append(line)
            #room for more stats later % etc

            sep = '\n'
            final = sep.join(listedstats)
            titlestring = ctx.author.name + "'s stats"
            embed = discord.Embed(title=titlestring,color=0x9062d3)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name="​", value=final, inline=False)
            sent = await ctx.send(embed=embed)
            await asyncio.sleep(7)
            await sent.delete()
            await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
            await ctx.message.add_reaction(emoji=tick) 
    
    
    #LISTENERS 

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.id) == '262371002577715201':
            textroll = random.randint(1,2000)
            if textroll  >= 1970:
                playerid = message.author.id
                playername = message.author.name
                try:
                    async with aiosqlite.connect('rolls.db') as db:
                        await db.execute("UPDATE rolltable SET rolls=rolls+1 WHERE user=?",[playerid])
                        await db.commit()
                    await message.add_reaction(emoji=plusone) 
                    channel = self.bot.get_channel(902418660767965184)
                    await channel.send(playername + " rolled: " + str(textroll))
                except:
                    print('no user')

    #LOOPS

    @tasks.loop(hours=2)
    async def freecummies(self):
        async with aiosqlite.connect('rolls.db') as db:
                await db.execute("UPDATE rolltable SET rolls=rolls+1")
                await db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        await dbget()

def setup(bot):
    bot.add_cog(rollsCog(bot))
    print('rolls cog loaded')

