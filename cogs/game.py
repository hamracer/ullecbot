import discord
from discord.ext import commands, tasks
import random

class diceCog(commands.Cog, name="game"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def game(self, ctx, *arg):


        z = random.randint(1,100)
        percentage_chance_for_ssr = 6
        if z < percentage_chance_for_ssr:
            ctx.message("")

def setup(bot):
    bot.add_cog(gameCog(bot))
    print('game cog loaded')