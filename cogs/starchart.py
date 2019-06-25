import discord
from discord.ext import commands

starcount = {}
channellist = [339155308767215618, 562352225423458326, 262371002577715201]


class starchartCog(commands.Cog, name="starchart"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
            # check if its the main channel
        if reaction.message.channel.id in channellist: 
                # check if reaction is a star
            if reaction.emoji == "⭐":
                react_id = reaction.message.id
                try:
                    starcount[react_id] += 1
                except:
                    starcount[react_id] = 1
            print(starcount)
            for i in starcount:
                if starcount[i] > 4:
                    nick = reaction.message.author.nick
                    









def setup(bot):
    bot.add_cog(starchartCog(bot))
    print('starchart cog loaded')