import discord
from discord.ext import commands


check = []
channellist = [339155308767215618]


class starchartCog(commands.Cog, name="starchart"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
            # check if its the main channel

        
        if reaction.message.channel.id in channellist: 
            # check if reaction is a star
            if reaction.emoji == "⭐" and len(await reaction.users().flatten()) >= 5:   
                react_id = reaction.message.id
                    # check if reaction is pinned already
                if react_id not in check:

                    check.append(react_id)
                    pfp = str(reaction.message.author.avatar_url)
                    nick = str(reaction.message.author)

                    guild_id = reaction.message.guild.id
                    channel_id = reaction.message.channel.id
                    message_id = reaction.message.id
                    content = reaction.message.content
                    
                    linkstr = "https://discordapp.com/channels/"+str(guild_id)+"/"+str(channel_id)+"/"+str(message_id)
                    titlestr = ">["+str(message_id)+"]("+str(linkstr)+")"
                    newcontent = titlestr + "\n\n" + content
                    


                        # for twitter or embeds
                    if reaction.message.embeds:
                        for i in reaction.message.embeds:
                            emauthor = i.author
                            emdescription = i.description
                           
                        emtwitter = "\n\n["+emauthor.name+"]"+"("+emauthor.url+")\n"+str(emdescription)
                        if content.strip(): 
                            newcontent = newcontent + emtwitter
                            embed = discord.Embed(color=0x9062d3, description=newcontent)    
                        else: 
                            titlestr = titlestr + emtwitter
                            embed = discord.Embed(color=0x9062d3, description=titlestr)

                        for i in reaction.message.embeds:
                            print("iterator")
                            emfields = i.fields
                            if emfields:
                                for o in emfields:
                                    embed.add_field(name=o.name, value=o.value, inline=o.inline)
                            emimage = i.image.url
                            try:
                                print("set image?")
                                emimage = emimage.strip("large")
                                emimage = emimage.strip(":")
                            except:
                                pass

                    if content.strip(): 
                        embed = discord.Embed(color=0x9062d3, description=newcontent)
                    else: 
                        embed = discord.Embed(color=0x9062d3, description=titlestr)
                                    
                    embed.set_thumbnail(url=pfp)
                    embed.set_author(name=nick)
                    embed.timestamp = reaction.message.created_at

                        # for attachments
                    if reaction.message.attachments:
                        file = reaction.message.attachments[0]
                        if file.url.lower().endswith(('.png', '.jpeg', '.jpg', '.gif', '.webp')):
                            embed.set_image(url=file.url)
                        elif file.url.lower().endswith(('.webm')):
                            embed.set_video(url=file.url)
                        else:
                            embed.add_field(name='Attachment', value=f'[{file.filename}]({file.url})', inline=False)

                    if reaction.message.embeds:
                        embed.set_image(url=emimage)


                        #find the starboard channel
                    for channel in reaction.message.guild.channels:
                        if str(channel) == "starboard":
                            await channel.send(embed=embed)





def setup(bot):
    bot.add_cog(starchartCog(bot))
    print('starchart cog loaded')
