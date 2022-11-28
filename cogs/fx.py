import discord
from discord.ext import commands
import json
import asyncio

channel_id=[1031516168365801482,339155308767215618],262371002577715201
calc_id=1046770057876869171

class fxCog(commands.Cog, name="fx"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in channel_id:
            if "//twitter.com" in message.content:
                print('detected twitter message')
                try:
                    if not message.embeds[0].video:
                        print('message has no video')
                        index = message.content.find('twitter')
                        newlink = message.content[:index] + 'vx' + message.content[index:]
                        testchannel = self.bot.get_channel(calc_id)
                        testlink = await testchannel.send(newlink)
                        #await asyncio.sleep(2)
                        try: 
                            if testlink.embeds[0].video:
                                print('vx has embed video')
                                sant = str(message.author) + " sent " + newlink
                                output = await message.channel.send(sant)
                                print('posted new link')
                                await message.delete()
                                print('deleted old link')
                            else:
                                print('vx has no embed video')
                                return
                        except:
                            print('vx has no embed video')
                            return
                    else:
                        print('message has a video')
                        return
                except:
                    print('message has embed video')
                    return
                    




    
def setup(bot):
    bot.add_cog(fxCog(bot))
    print('fx cog loaded')