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

data =[]

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
    async def cum(self, ctx):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
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
                    await ctx.reply(roll)
                    await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                    await ctx.message.add_reaction(emoji=tick) 
                    
            else: 
                await ctx.reply("u got no cums loser")
                await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                await ctx.message.add_reaction(emoji=tick) 
                

    @commands.command()
    async def cum10(self, ctx):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
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
                    n = 10
                    totalrolls = []
                    while n > 0:
                        n -= 1 
                        roll = await rolling(playerid)
                        totalrolls.append(roll)
                    sendies = (', '.join('%s x%d' % (item, count) for item, count in sorted(Counter(totalrolls).items())))
                    await ctx.reply(umproll + umproll + umproll)
                    await ctx.reply(sendies)
                    await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                    await ctx.message.add_reaction(emoji=tick) 
            else: 
                await ctx.reply("u dont got enough cums loser")
                await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                await ctx.message.add_reaction(emoji=tick) 

    @commands.command()
    async def howmanycumsdoihaveleft(self, ctx):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
            playerid = ctx.author.id
            data = await dbget()
            try:
                match = next((item for item in data if item['user'] == playerid), 'Nothing Found') 
                await ctx.reply("You have " + str(match['rolls']) + " cums left.")
            except:
                await ctx.reply("You're not on the cummies list, please cum once first.")

    
    #@commands.command()
    #async def donate(self, ctx, arg1, arg2):
    #    data = await dbget()

    #GAMES

    @commands.command()
    async def dice(self, ctx, arg):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
            data = await dbget()
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
                    embed.add_field(name='You lose!!', value="You lost "+ arg +" rolls", inline=False)
                if playersum > botsum:
                    embed.add_field(name='You win!!', value="You win "+ arg +" rolls", inline=False)
                    arg = int(arg) + int(arg)
                    await db.execute("UPDATE rolltable SET rolls=rolls+? WHERE user=?",(arg,playerid))
                if botsum == playersum:
                    embed.add_field(name='You draw!!', value="Your rolls have been returned", inline=False)
                    await db.execute("UPDATE rolltable SET rolls=rolls+? WHERE user=?",(arg,playerid))
                await db.commit()
                await sent.edit(embed=embed)
            else:
                await ctx.reply("You dont have enough rolls for this.")
        #except:
        #    print("something went wrong")


    #STATS

    @commands.command()
    async def cumsavers(self, ctx):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
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
            embed.add_field(name="​", value=sep.join(display), inline=False)
            await ctx.send(embed=embed)

    @commands.command()
    async def cumstats(self, ctx):
        if str(ctx.channel.id) == '853625002779869204' or '562352225423458326':
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
            await ctx.send(embed=embed)
    
    
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

