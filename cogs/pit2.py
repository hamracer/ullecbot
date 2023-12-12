import discord
from discord.ext import commands
import json
import asyncio
import time



class pit2Cog(commands.Cog, name="pit2"):

    def __init__(self, bot):
        self.bot = bot

    def loadconfig():
        global pit2channel
        pit2channel=1184062256296771584
        
    loadconfig()

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
            await cage.send("Welcome to your cage, you have been timed out for 10 minutes")

async def setup(bot):
    await bot.add_cog(pit2Cog(bot))
    print('pit2 cog loaded')
