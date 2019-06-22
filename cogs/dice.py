import discord
from discord.ext import commands
import random


class diceCog(commands.Cog, name="dice"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, arg):
        

def setup(bot):
    bot.add_cog(diceCog(bot))
    print('dice cog loaded')