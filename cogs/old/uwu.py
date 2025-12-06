import discord
from discord.ext import commands
import json

channel_id=[339155308767215618,600074573127352361]
uwu=[]

class uwuCog(commands.Cog, name="uwu"):
    def __init__(self, bot):
        self.bot = bot

    def loaduwu():

        global uwu

        try:
            with open('configs/uwu.json', encoding='utf-8') as f:
                print('loading uwu list')
                data = json.load(f)
                uwu = data['wepwace']
            return True
        except Exception as e:
            print('Exception: ' + str(e))
            return False

    loaduwu()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.id == 613716331656642570:
            channel = self.bot.get_channel(payload.channel_id)
            if channel.guild.get_member(payload.user_id).guild_permissions.manage_messages:
                mess = await channel.fetch_message(payload.message_id)
                listedcontent = (mess.content).lower()
                for i in uwu:
                    ori = i["t"]
                    rep = i["r"]
                    listedcontent = listedcontent.replace(ori,rep)
                await channel.send(listedcontent)
                



    
async def setup(bot):
    await bot.add_cog(uwuCog(bot))
    print('uwu cog loaded')