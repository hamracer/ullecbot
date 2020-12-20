import discord
from discord.ext import tasks, commands
import asyncio



class containmentCog(commands.Cog, name="containment"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def cya(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name='forced containment')
        tp = discord.utils.get(ctx.guild.roles, name='ToriPoster')
        print(ctx.message.guild.members)
        for member in ctx.message.guild.members:
            print("looping through member list")
            print(member)
            if tp in member.roles:
                print("checking for tp")
                await member.add_roles(role)
                await ctx.channel.send(f'{member} has been contained <:umagun:579673776929636352>')
        minutes = 3 * 60

        await asyncio.sleep(minutes)
        for member in ctx.message.guild.members:
            if role in member.roles:
                await member.remove_roles(role)

def setup(bot):
    bot.add_cog(containmentCog(bot))
    print('containment cog loaded')

