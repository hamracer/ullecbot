import discord
from discord.ext import commands

starcount = {}
checklist = []
channellist = [339155308767215618, 562352225423458326, 262371002577715201]


class starchartCog(commands.Cog, name="starchart"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
            # check if its the main channel
        if reaction.message.channel.id in channellist: 
                # check if reaction is a star
            if reaction.emoji == "⭐":
                react_id = reaction.message.id           
                print("we see the star")
                    # for users on the reaction list
                async for rusers in reaction.users():
                    try:
                        print("getting last user")
                        for i in starcount[react_id]:
                            if rusers.id is not i:
                                print("ruser id")
                                print(rusers.id)
                                starcount[react_id].append(rusers.id)
                                print("appending to list")
                                    # remove dupes coz i dont know why there are dupes im dumb
                                starcount[react_id] = list(dict.fromkeys(starcount[react_id]))
                                
                            else:
                                print("dont append to list")
                    # if we don't find a message in the dict created an instance for it
                    except:
                        starcount[react_id] = [rusers.id]
                        print("creating new listing")

            print(starcount)
            for i in starcount:
                    # if there are 5 or more stars
                if len(starcount[i]) == 5:
                    if react_id not in checklist:
                        checklist.append(react_id)
                        nick = reaction.message.author
                        pfp = reaction.message.author.avatar_url

                            # setup the embed
                        guild_id = reaction.message.guild.id
                        channel_id = reaction.message.channel.id
                        message_id = reaction.message.id
                        content = reaction.message.content
                        linkstr = "https://discordapp.com/channels/"+str(guild_id)+"/"+str(channel_id)+"/"+str(message_id)
                        titlestr = "> ["+str(message_id)+"]("+str(linkstr)+")"
                        embed = discord.Embed(color=0x9062d3, description=titlestr)
                        embed.set_thumbnail(url=pfp)
                        embed.set_author(name=nick)
                        if content.strip(): 
                            embed.add_field(name='\u200b', value=content)

                            # for attachments
                        if reaction.message.attachments:
                            file = reaction.message.attachments[0]
                            if file.url.lower().endswith(('png', 'jpeg', 'jpg', 'gif', 'webp')):
                                embed.set_image(url=file.url)
                            else:
                                embed.add_field(name='Attachment', value=f'[{file.filename}]({file.url})', inline=False)
                        
                            #find the starboard channel
                        for channel in reaction.message.guild.channels:
                            if str(channel) == "starboard":
                                await channel.send(embed=embed)





def setup(bot):
    bot.add_cog(starchartCog(bot))
    print('starchart cog loaded')