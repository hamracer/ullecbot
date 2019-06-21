import discord
from discord.ext import commands
import random
import json


snailarmy = []

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
        percentage_chance = 6
        if reaction.emoji == "🐌":
            z = random.randint(1,100)
            print(user)
            print(z)
            if z < percentage_chance:
                x = random.randrange(0, 8)
                for val in snailarmy[x:len(snailarmy)]:
                    await reaction.message.add_reaction(emoji=val)


    @commands.Cog.listener()
    async def on_message(self, message): #  used to check emotes in test channel
        if message.channel.id == 585758519500865546:
            print(message.content)




def setup(bot):
    bot.add_cog(snailCog(bot))
    print('snail cog loaded')
