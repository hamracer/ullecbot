import discord
from discord.ext import commands, tasks
import json, random
import asyncio
import aiosqlite
from collections import Counter

gbfgid = '339155308767215618'
borpaspin = '<a:borpaspin:905835451204640829>'

plusone = '<:plusone:899989682555854868>'
loading = '<a:loading:902407104499974144>'
tick = '<:tick:902416135683702794>'
umproll = '<a:umproll:903953063746883614>'

data =[]

def rolling(test=False):
    
    if test is False:
        theroll = random.randint(1,100)
    else: 
        theroll = int(test)

    if theroll > 99:
        roll = "https://cdn.discordapp.com/attachments/262371002577715201/875547855648079872/unknown.png"
        return roll
    if theroll >= 94:
        roll = borpaspin
        return roll
    else:
        roll = "cum"
        return roll
    
async def dbget():
    global data
    db = await aiosqlite.connect('rolls.db')
    cursor = await db.execute('SELECT user, rolls FROM rolltable')
    rows = await cursor.fetchall()
    data = [{'user': a,'rolls': b,} for a,b in rows]
    print("dbget - finished")
    return data

class rollsCog(commands.Cog, name="rolls"):
    def __init__(self, bot):
        self.bot = bot
        self.freecummies.start()
        

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def ct(self,ctx):
        async with aiosqlite.connect('rolls.db') as db:
                await db.execute("CREATE TABLE rolltable (user INT UNIQUE, rolls INT, totalrolls INT, cums INT, borpas INT)")
                await db.commit()
                print("table created")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def dt(self,ctx):
            async with aiosqlite.connect('rolls.db') as db:
                await db.execute("DROP TABLE rolltable")
                await db.commit()
                print("table dropped")


    @commands.command()
    async def cum(self, ctx):
        if str(ctx.channel.id) == '262371002577715201' or '562352225423458326':
            await ctx.message.add_reaction(emoji=loading) 
            global data
            playerid = ctx.author.id
            #check if author is in db
            if any(i['user'] == playerid for i in data):
                print("player exists: " + str(playerid)) 
            else:
                #add author to db
                async with aiosqlite.connect('rolls.db') as db:
                    await db.execute("INSERT INTO rolltable VALUES (?, ?);", (playerid, 4))
                    await db.commit()
                    await ctx.reply("Look here everyone a new cummer!")
            #get updated db value
            await dbget()
            match = next((item for item in data if item['user'] == playerid), 'Nothing Found')
            if int(match['rolls']) > 0:
                async with aiosqlite.connect('rolls.db') as db:
                    await db.execute("UPDATE rolltable SET rolls=rolls-1 WHERE user=?",[playerid])
                    await db.commit()
                    roll = rolling()
                    await ctx.reply(roll)
                    await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                    await ctx.message.add_reaction(emoji=tick) 
            else: 
                await ctx.reply("u got no cums loser")
                await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
                await ctx.message.add_reaction(emoji=tick) 

    @commands.command()
    async def cum10(self, ctx):
        if str(ctx.channel.id) == '262371002577715201' or '562352225423458326':
            await ctx.message.add_reaction(emoji=loading) 
            global data
            playerid = ctx.author.id
            #check if author is in db
            if any(i['user'] == playerid for i in data):
                print("player exists: " + str(playerid)) 
            else:
                await ctx.reply("u got no cums loser")
                return

            #get updated db value
            await dbget()
            match = next((item for item in data if item['user'] == playerid), 'Nothing Found')
            if int(match['rolls']) >= 10:
                async with aiosqlite.connect('rolls.db') as db:
                    await db.execute("UPDATE rolltable SET rolls=rolls-10 WHERE user=?",[playerid])
                    await db.commit()
                    n = 10
                    totalrolls = []
                    while n > 0:
                        n -= 1 
                        roll = rolling()
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
        if str(ctx.channel.id) == '262371002577715201' or '562352225423458326':
            playerid = ctx.author.id
            await dbget()
            try:
                match = next((item for item in data if item['user'] == playerid), 'Nothing Found') 
                await ctx.reply("You have " + str(match['rolls']) + " cums left.")
            except:
                await ctx.reply("You're not on the cummies list, please cum once first.")

    #@commands.command()
    #async def cumsavers(self, ctx):



    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def testadd(self, ctx, arg):
        userid = ctx.author.id
        async with aiosqlite.connect('rolls.db') as db:
            try: 
                await db.execute("UPDATE rolltable SET rolls=rolls+? WHERE user=?", (int(arg), userid))
                await db.commit()
            except: 
                print("failed to write to db")

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.id) == '262371002577715201':
            textroll = random.randint(1,2000)
            if textroll  >= 1970:
                playerid = message.author.id
                playername = message.author.name
                try:
                    async with aiosqlite.connect('rolls.db') as db:
                        await db.execute("UPDATE rolltable SET rolls=rolls-10 WHERE user=?",[playerid])
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

