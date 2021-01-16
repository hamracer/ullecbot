import discord
from discord.ext import commands, tasks
import random

channellist = [508905628652142592, 339235017760833536, 508225092530995220, 339155308767215618, 339879301639962656]
rolllist = []


class diceCog(commands.Cog, name="dice"):
    def __init__(self, bot):
        self.bot = bot
        self.clear.start()

    def dice(self, sides):
        roll = random.randint(1,sides)
        return str(roll)



# the idea is you can choose the number of dice and what dice to roll
    @commands.command()
    async def roll(self, ctx, *arg):

        global rolllist
        print(rolllist)
        if ctx.author.id in rolllist:
            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
            return

        else:
            if ctx.channel.id in channellist: 
                r = 0
                resultnum = 0
                output = []
                author = ctx.author.name
                titlestring = author + " just rolled the dice 🎲 \n"
                embed = discord.Embed(color=0x9062d3)
                embed.set_author(name="ullec bot")
                embed.set_thumbnail(url=ctx.author.avatar_url)
                try:
                    if len(arg) > 2:
                        raise Exception
                    if len(arg) == 1:
                        try:
                            b = arg[0]
                            b = b.strip("d")
                            b = int(b)
                            result = self.dice(b)
                            rolls = 1
                        except:
                            b = arg[0]
                            c = b.split("d")
                            b = int(c[1])
                            result = self.dice(b)
                            rolls = int(c[0])
                    if len(arg) == 2:
                        for id, i in enumerate(arg):
                            g = arg[id]
                            if "d" in g:
                                b = g
                                b = b.strip("d")
                                b = int(b)
                                if id == 0:
                                    rolls = int(arg[1])
                                if id == 1:
                                    rolls = int(arg[0])

                            pass
                    while rolls > r:
                        r += 1
                        result = self.dice(b)
                        resultnum = resultnum + int(result)
                        resultstring = "You rolled "+ result+"/"+str(b)
                        output.append(resultstring)
                    if b > 100:
                        raise Exception
                    if rolls > 14:
                        raise Exception

                    foutput = '\n'.join(output)
                    embed.insert_field_at(index=1, name=titlestring, value=foutput)
                    print(str(resultnum) + " " + str(rolls) + " " + str(b))
                    totalstr = "Total: " + str(resultnum) + " Average: " + str(round(int(resultnum)/int(rolls),2)) + " Percentile: " + str(int(int(resultnum) * 100 / (int(rolls) * int(b))))
                    embed.insert_field_at(index=5, name=totalstr, value="\u200b", inline=False)
                    await ctx.send(embed=embed)
                    rolllist.append(ctx.author.id)
                    
                except Exception as e:
                    print('Exception: ' + str(e)) 
                    await ctx.message.add_reaction(emoji=':worst:579662420537114626')

    @tasks.loop(minutes=1)
    async def clear(self):
        global rolllist
        rolllist=[]
        

def setup(bot):
    bot.add_cog(diceCog(bot))
    print('dice cog loaded')
