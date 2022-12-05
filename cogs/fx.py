import discord
from discord.ext import commands
import json
import asyncio

#channel_id=[1031516168365801482,262371002577715201]
channel_id=[1031516168365801482,339155308767215618,262371002577715201]
calc_id=1046770057876869171

class fxCog(commands.Cog, name="fx"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in channel_id:
            if "//twitter.com" in message.content:
                print('detected twitter message') 
                index = message.content.find('twitter')
                newlink = message.content[:index] + 'vx' + message.content[index:] #generate vx link
                testchannel = self.bot.get_channel(calc_id) 
                testlink1 = await testchannel.send(newlink) #send to the test channel 
                await asyncio.sleep(2)
                
                print('|||----LOOK FOR SUCCESS----|||')
                try:
                    if testlink1.embeds:
                        print('testlink1 = success')
                        print('|||----LOOK FOR SUCCESS----|||')
                        testlink2 = testlink1
                    
                    else:
                        print('first one failed')
                        print('trying again')
                        testlink2 = await testchannel.send(newlink) #send to the test channel
                        if testlink2.embeds:
                            print('testlink2 = success')
                            print('|||----LOOK FOR SUCCESS----|||')
                except:
                    print('might not have an embed')
                try:
                    if testlink2.embeds[0].video: #if the link has a video
                        print('video does exist')
                        sant = str(message.author) + " - " + newlink
                        output = await message.channel.send(sant) #send link to channel
                        await output.edit(content=(message.author.mention) + " - " + newlink)
                        await message.delete() #delete first message
                        return

                    else:
                        print('video does not exist')
                except Exception as e:
                    print('Exception: ' + str(e)) 

                    
    
async def setup(bot):
    await bot.add_cog(fxCog(bot))
    print('fx cog loaded')