import discord
from discord.ext import commands
import random
import json
import asyncio


snailarmy = []
nolist = [] 

class snailCog(commands.Cog, name="snail"):
    def __init__(self, bot):
        self.bot = bot

    def loadconfig():
        global snailarmy

        try:
            with open('configs/emoji.json', 'r') as f:
                print('loading emoji config for snail cog')
                data = json.load(f)
                snailarmy = data['snailarmy']
            return True
        except Exception as e:
            print('Exception: ' + str(e))
            return False

    loadconfig()



    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        try:
            role = discord.utils.get(user.guild.roles, name="nitrocucks")
        except:
            pass

        if reaction.emoji == "🐌" and role in reaction.message.author.roles:
            await reaction.message.remove_reaction("🐌",user)

        if reaction.emoji == "😁":
            authorroles = reaction.message.author.roles
            print(authorroles)
            print(role)
        
        elif reaction.emoji == "🐌" and reaction.message.guild.get_member(user.id).guild_permissions.manage_messages and user.id not in nolist:
            z = random.randint(1,100)
            percentage_chance_for_mod = 33
            if z < percentage_chance_for_mod:
                x = random.randrange(0, 8)
                for val in snailarmy[x:len(snailarmy)]:
                    await reaction.message.add_reaction(emoji=val)

        elif reaction.emoji == "🐌" and user.id not in nolist:
            z = random.randint(1,100)
            percentage_chance = 6
            if z < percentage_chance:
                x = random.randrange(0, 8)
                for val in snailarmy[x:len(snailarmy)]:
                    await reaction.message.add_reaction(emoji=val)
        

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        user = channel.guild.get_member(payload.user_id)
        nolist.append(user.id)
        await asyncio.sleep(30)
        nolist.remove(user.id)



def setup(bot):
    bot.add_cog(snailCog(bot))
    print('snail cog loaded')
