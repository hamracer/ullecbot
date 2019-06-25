import discord
from discord.ext import commands

check = []
channellist = [562352225423458326, 262371002577715201]


class starchartCog(commands.Cog, name="starchart"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
            # check if its the main channel

        
        if reaction.message.channel.id in channellist: 
            # check if reaction is a star
            if reaction.emoji == "⭐" and len(await reaction.users().flatten()) >= 2:   
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
                    
                    if content.strip(): 
                        embed = discord.Embed(color=0x9062d3, description=newcontent)
                    else: 
                        embed = discord.Embed(color=0x9062d3, description=titlestr)
                    embed.set_thumbnail(url=pfp)
                    embed.set_author(name=nick)

                        # for attachments
                    if reaction.message.attachments:
                        file = reaction.message.attachments[0]
                        if file.url.lower().endswith(('.png', '.jpeg', '.jpg', '.gif', '.webp')):
                            dict['image'] = {'url':file.url}
                        elif file.url.lower().endswith(('.webm')):
                            dict['video'] = {'url':file.url, 'height':0, 'width':0}
                        else:
                            dict['fields'].append({'inline': True, 'name':'Attachment', 'value':f'[{file.filename}]({file.url})'})
                    
                    
                        #find the starboard channel
                    for channel in reaction.message.guild.channels:
                        if str(channel) == "starboard":
                            await channel.send(embed=embed)





def setup(bot):
    bot.add_cog(starchartCog(bot))
    print('starchart cog loaded')