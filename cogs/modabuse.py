import discord
from discord.ext import commands
import random


class modabuseCog(commands.Cog, name="modabuse"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 157623260526280704:
            await message.author.edit(nick="zbanned idiot")




def setup(bot):
    bot.add_cog(modabuseCog(bot))
    print('modabuse cog loaded')