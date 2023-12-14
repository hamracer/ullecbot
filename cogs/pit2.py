import discord
from discord.ext import commands
import random
import asyncio



class pit2Cog(commands.Cog, name="pit2"):

    def __init__(self, bot):
        self.bot = bot

    def loadconfig():
        global pit2channel
        pit2channel=1184062256296771584
        
    loadconfig()



    
    async def countdown(self, timer, xcage):
        print(timer)
        while timer > 5:
            if timer%60 == 0:
                await xcage.send(f"You have {timer} seconds remaining")
            await asyncio.sleep(1)
            timer -= 1
            print(timer)
        else:
            #close thread
            print("closing")
            await xcage.send(f"This cage is closing in {timer} seconds")
            await asyncio.sleep(5)
            await xcage.delete()

    @commands.Cog.listener()
    async def on_member_update(self, before:discord.Member, after:discord.Member):
        channel = self.bot.get_channel(int(pit2channel))
        role = before.guild.get_role(1184070134751559690)
        if role in after.roles and role not in before.roles:
            print('pit2 found')
            cage = await channel.create_thread(
                name=str(after.name) + "'s cage",
                type=discord.ChannelType.public_thread
            )
            await cage.send("Welcome to your cage, you have been timed out for 65 seconds")
            # add timer 6 minutes
            # roll for + +3, - 2 minutes
            # show time on every x
            await self.countdown(timer=65,xcage=cage)

async def setup(bot):
    await bot.add_cog(pit2Cog(bot))
    print('pit2 cog loaded')
