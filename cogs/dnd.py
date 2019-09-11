import discord
from discord.ext import commands, tasks
import random

approved_channel=[508225092530995220,610116940064882689]
genlist=[]

class dndCog(commands.Cog, name="dnd"):
    def __init__(self, bot):
        self.bot = bot
        self.clear.start()

    def dice(self, sides):
        roll = random.randint(1,sides)
        return int(roll)

    @commands.command()
    async def cgen(self, ctx):
        global genlist
        if ctx.author.id in genlist:
            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
            return

        else:
            if ctx.channel.id in approved_channel:
                genlist.append(ctx.author.id)
                rolls = []
                total = []
                
                for _ in range(6):
                    stat = []
                    for _ in range(4):
                        roller = self.dice(6)
                        stat.append(roller)
                    rolls.append(stat)
                output = []
                for i in rolls:
                    drop = min(i)
                    o = i.copy()
                    i.remove(min(i))
                    perdie = str(str(o[0]) + " + " + str(o[1]) + " + " + str(o[2]) + " + " + str(o[3]) + " (drop " + str(drop) + ")" + " = " + str(sum(i)))
                    total.append(sum(i))
                    
                    
                    output.append(perdie)
                    foutput = '\n'.join(output)

                embed = discord.Embed(color=0x9062d3)
                author = ctx.author.name
                titlestring = author + " is rolling 🎲🎲🎲"
                embed.insert_field_at(index=1, name=titlestring, value=foutput)
                percentile = int(sum(total) / 108 * 100)
                stats = "---------------------------------"
                after = str(percentile)[-1]
                if after == "1":
                    end = "st"
                elif after == "2":
                    end = "nd"
                elif after == "3":
                    end = "rd"
                else:
                    end = "th"
                
                statstring = "This roll ranks at the " + str(percentile) + end +" percentile"
                embed.insert_field_at(index=3, name=stats, value=statstring, inline=False)
                await ctx.send(embed=embed)
            
    @tasks.loop(minutes=5)
    async def clear(self):
        global genlist
        genlist=[]


def setup(bot):
    bot.add_cog(dndCog(bot))
    print('dnd cog loaded')