import discord
from discord.ext import commands

user = None
msgr = None
approved_channel=[339235017760833536]

class muriCog(commands.Cog, name="muri"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("muripals")
    async def muri(self, ctx, arg1):
        if ctx.channel.id in approved_channel:
            arg1 = arg1.strip("<@")
            try:
                arg1 = arg1.strip("!")
            except:
                pass
            userid = arg1.strip(">")
            userid = int(userid)
            

            await ctx.message.add_reaction(emoji=':muri:590937344299761665')
            global user
            global msgr
            user = userid
            msgr = ctx.message.id
        
        else:

            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        global user
        global msgr
        if payload.message_id == msgr:
            if payload.user_id == user:
                if payload.emoji.id == 590937344299761665:
                    channel = self.bot.get_channel(payload.channel_id)
                    user2 = channel.guild.get_member(user)
                    role = discord.utils.get(channel.guild.roles, name='muripals')
                    await user2.add_roles(role)

def setup(bot):
    bot.add_cog(muriCog(bot))
    print('muri cog loaded')

