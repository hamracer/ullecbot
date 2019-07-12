import discord
from discord.ext import commands

gbfgid = '339155308767215618'


class echoCog(commands.Cog, name="echo"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.id) == '599327014146539520':
            gbfg = self.bot.get_channel(int(gbfgid))
            await gbfg.send(message.content) 

def setup(bot):
    bot.add_cog(echoCog(bot))
    print('echo cog loaded')

