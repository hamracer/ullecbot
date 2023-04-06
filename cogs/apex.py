import discord
from discord.ext import commands
import json
import asyncio
import requests
import datetime



class apexCog(commands.Cog, name="apex"):
    def __init__(self, bot):
        self.bot = bot


    def loadtoken():
        # load globals defined in the config file

        global token

        try:
            with open('configs/apexapi.json') as f:
                print('loading apex api')
                data = json.load(f)
                token = data['token']
                return True
        except:
            print('no api')
            return True

    loadtoken()


    @commands.command()
    async def ranked(self, ctx):
        r = requests.get('https://api.mozambiquehe.re/maprotation?auth=' + token + '&version=2').json()
        currentmap = r["ranked"]["current"]["map"]
        nextmap = r["ranked"]["next"]["map"]
        timeleft = r["ranked"]["current"]["remainingTimer"]
        asset = r["ranked"]["current"]["asset"]

        embed=discord.Embed(title='Apex Legends - Ranked')
        embed.set_thumbnail(url=asset)
        embed.add_field(name='Current Map', value=currentmap, inline=True)
        embed.add_field(name='Time Left', value=timeleft, inline=True)
        embed.add_field(name='Next Map', value=nextmap, inline=True)
        await ctx.send(embed=embed)
    

async def setup(bot):
    await bot.add_cog(apexCog(bot))
    print('apex cog loaded')

