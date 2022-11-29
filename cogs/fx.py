import discord
from discord.ext import commands
import json
import asyncio

channel_id=[1031516168365801482,262371002577715201]
#channel_id=[1031516168365801482,339155308767215618,262371002577715201]
calc_id=1046770057876869171

class fxCog(commands.Cog, name="fx"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in channel_id:
            if "//twitter.com" in message.content:
                print('detected twitter message')
                await asyncio.sleep(2)
                try:
                    print('test to see if link does not have a video')
                    if not message.embeds[0].video:
                        print('original has no video')
                        index = message.content.find('twitter')
                        newlink = message.content[:index] + 'vx' + message.content[index:]
                        testchannel = self.bot.get_channel(calc_id)
                        testlink = await testchannel.send(newlink)
                        try:
                            if testlink.embeds[0].video:
                                sant = str(message.author) + " - " + newlink
                                output = await message.channel.send(sant)
                                await output.edit(content=(message.author.mention) + " - " + newlink)
                                await message.delete()
                                await testlink.delete()
                        except:
                            print('testlink has no video')
                            print('nothing to be done')
                            return

                    if message.embeds[0].video:
                        print('original has a video')
                        index = message.content.find('twitter') #find twitter in string
                        newlink = message.content[:index] + 'vx' + message.content[index:] #add vx to string
                        sant = str(message.author) + " - " + newlink #create new string to post with new vxtwitter link
                        output = await message.channel.send(sant) #send link to channel
                        await output.edit(content=(message.author.mention) + " - " + newlink) #edit link with mention
                        await message.delete()
                        
                        
                except:
                    print('something went wrong')
                    return
                    




    
async def setup(bot):
    await bot.add_cog(fxCog(bot))
    print('fx cog loaded')