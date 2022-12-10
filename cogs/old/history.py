import discord
from discord.ext import commands
import re

class historyCog(commands.Cog, name="history"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def ban(self, ctx, *args):
        arg = (" ".join(args[:]))
        channel = ctx.channel
        files = []
        texts = []
        files.append("Vote for the following users to be banned:")
        async for message in channel.history(limit=200):
            content = message.content
            author = message.author.name+"#"+message.author.discriminator
            if message.id == ctx.message.id:
                print('dont ban the admin')
            elif message.author.id is self.bot.user.id:
                print('dont ban the bot')
            else:
                if arg in content:
                    files.append(author)
        files = list(dict.fromkeys(files))
        for says in files:
            texts.append(says)
        mess = '\n'.join(texts)
        thismessage = await ctx.send(mess)
        await thismessage.add_reaction(emoji=':best:579662404980572161')
        await thismessage.add_reaction(emoji=':worst:579662420537114626')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        


def setup(bot):
    bot.add_cog(historyCog(bot))
    print('history cog loaded')
