import discord
from discord.ext import commands
import json
import random
import asyncio

#active channel list
channel_id=[1446500430954631359,262371002577715201]

#emoji list
loading = '<a:loading:902407104499974144>'
borpaspin = '<a:borpaspin:905835451204640829>'
goldborpaspin = '<a:goldborpaspin:906324859007696916>'
borpa = '<:borpa:1446834792934015089>'
ldash = '<:ldash:727000991097946112>'
blank = '<:blank:525377105308024853>'
mpreg = '<:mpregful:1409028460667605154>'
cum = '<a:CUM:1446834290989203619>'


async def rolling():
    print("rolling")
    r1=random.randint(1,100)
    print(r1)
    if r1>50:
        roll=borpaspin
        r2=random.randint(1,100)
        print(r2)
        if r2>50:
            roll=borpaspin
            r3=random.randint(1,100)
            print(r3)
            if r3>50:
                roll=goldborpaspin
    else:
        roll=borpa
    print(roll)
    return roll
    

class cuemCog(commands.Cog, name="cuem"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    #@commands.cooldown(1, 30, commands.BucketType.user)
    @commands.is_owner()
    async def cum2(self, ctx):
        if ctx.channel.id in channel_id:
            print("channel=true")
            await ctx.message.add_reaction('✅')
            
            #gacha time
            roll= await rolling()
            if roll==borpa:
                dmg = random.randint(1,10)
                dmg_roll=f"rolling 1d10"
                dmg_text=f"{dmg} damage dealt!"
            elif roll==borpaspin:
                dmg = random.randint(1,100)
                dmg_roll=f"rolling 1d100"
                dmg_text=f"{dmg} damage dealt!"
            elif roll==goldborpaspin:
                dmg = random.randint(1,10000)
                dmg_roll=f"rolling 1d10000"
                dmg_text=f"{dmg} damage dealt!"  
            battle=roll+blank+blank+blank+mpreg
            status="Preparing to cum..."
            line1 = await ctx.reply(battle)
            line2 = await ctx.send("-------------------------------------")
            line3 = await ctx.send(status)
        
            await asyncio.sleep(1)
            battle=blank+roll+blank+blank+mpreg
            status=dmg_roll
            await line1.edit(content=battle)
            await line3.edit(content=status)

            await asyncio.sleep(1)
            battle=blank+blank+roll+blank+mpreg
            await line1.edit(content=battle)

            await asyncio.sleep(1)
            battle=blank+blank+blank+roll+mpreg
            await line1.edit(content=battle)

            await asyncio.sleep(1)
            battle=blank+blank+blank+cum+mpreg
            status=dmg_text
            print(dmg_text)
            await line1.edit(content=battle)
            await line3.edit(content=status)

            await asyncio.sleep(1)
            battle=blank+blank+blank+blank+mpreg
            await line1.edit(content=battle)

        else:
            pass

    
    
async def setup(bot):
    await bot.add_cog(cuemCog(bot))
    print('cuem cog loaded')

####
# The idea of this is to make a 5x5? slot machine or something similar
#
# spinner will spin to do dmg to a boss 
#