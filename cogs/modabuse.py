import discord
from discord.ext import commands
import random
import gspread
import json
import os


def loadgspread():
    
    try:
        gc = gspread.service_account(filename='configs/blissful-land-240720-c3abbb49b748.json')

    except:
        scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
        json_creds = os.environ.get('gspread_creds')
        creds_dict = json.loads(json_creds)
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
        gc = gspread.authorize(creds)

    sh = gc.open('botstuff')
    nopermslist = sh.sheet1.col_values(2)
    return nopermslist


class modabuseCog(commands.Cog, name="modabuse"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name="look at this retard")
        nopermslist = loadgspread()
        print(nopermslist)
        for i in nopermslist:
            print(i)
            print(member.id)
            if member.id == int(i):
                await member.add_roles(role)


        




def setup(bot):
    bot.add_cog(modabuseCog(bot))
    print('modabuse cog loaded')