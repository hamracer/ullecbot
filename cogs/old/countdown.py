import discord
from discord.ext import commands
import time
from datetime import datetime, timezone, timedelta




class countdownCog(commands.Cog, name="countdown"):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(name='whendoesthemegaquakehappen', aliases=['howlongleftuntiligetonaplaneforjapan'])
    async def howlongleftuntiligetonaplaneforjapan(self, ctx):
        futuredate = datetime.strptime("28/8/2024 11:10:00","%d/%m/%Y %H:%M:%S")
        timezone_offset = +10.0  # Pacific Standard Time (UTC−08:00)
        tzinfo = timedelta(hours=timezone_offset)
        nowdate = datetime.utcnow() + tzinfo
        countdown = futuredate - nowdate
        s = countdown.total_seconds()
        seconds_to_minute   = 60
        seconds_to_hour     = 60 * seconds_to_minute
        seconds_to_day      = 24 * seconds_to_hour

        days    =   s // seconds_to_day
        s    %=  seconds_to_day

        hours   =   s // seconds_to_hour
        s    %=  seconds_to_hour

        minutes =   s // seconds_to_minute
        s    %=  seconds_to_minute

        seconds = s

        await ctx.reply("%d days, %d hours, %d minutes, %d seconds" % (days, hours, minutes, seconds))



    
    
async def setup(bot):
    await bot.add_cog(countdownCog(bot))
    print('countdown cog loaded')
