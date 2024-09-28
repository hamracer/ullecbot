import discord
from discord.ext import commands
from NyaaPy import Nyaa
import datetime
from collections import defaultdict
import requests
import json
import pytz


weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
pacificTime = pytz.timezone("Etc/GMT-7")

channel_id = None
server_id = None

class animeCog(commands.Cog, name="anime"):
    dict_of_anime = None

    def __init__(self, bot):
        self.bot = bot

        if not self.dict_of_anime:
            print('bulding anime shit')
            self.dict_of_anime = self.dict_builder()

        self.loadconfig()

    def loadconfig(self):
        global channel_id
        global server_id

        try:
            with open('configs/config.json') as f:
                print('loading config for animecog')
                data = json.load(f)
                channel_id = data['channel_id']
                server_id = data['server_id']
            return True
        except Exception as e:
            print('Exception: ' + str(e))
            return False



    def dict_builder(self):
        query = '''
                query {
                    MediaListCollection(userName:"notcellu" type:ANIME status:CURRENT){
                        lists{
                            entries{
                                media{
                                    title{
                                        romaji
                                    }
                                    nextAiringEpisode{
                                            airingAt
                                    }
                                }
                            }
                        }
                    }
                }
            '''
        url = 'https://graphql.anilist.co'

        # Make the HTTP Api request
        response = requests.post(url, json={'query': query})

        data = response.json()

        output = defaultdict(list)
        print(output)

        for show in data['data']['MediaListCollection']['lists'][0]['entries']:
            title = (show['media']['title']['romaji'])
            print("Title: " + str(title))
            try:
                airing = (show['media']['nextAiringEpisode']['airingAt'])
                print("Raw Airing: " + str(airing))
                air_date = (datetime.datetime.utcfromtimestamp(airing))
                print("Airing: " + str(air_date))
                output[weekdays[air_date.astimezone(pacificTime).weekday()]].append(title)
            except:
                pass

            #  dictionary called output, inside list of weekdays, inside a list of days derived from the air_date
        print(output)
        return output


    async def animeEmbedOutput(self, ctx, listSlice, title):
        outputList = '\n'.join(listSlice)
        embed = discord.Embed()
        embed2 = discord.Embed()
        print(len(outputList))
        if (len(outputList)) > 1000:
            splity = outputList.split("**[Friday]**")
            splity1 = splity[0]
            splity2 = splity[1]
            splity2 = "**[Friday]**" + splity2
            title1 = 'ANIME 1 <:naneggu:564053655775346699>' 
            title2 = 'ANIME 2 <:naneggu:564053655775346699>' 
            embed.add_field(name=title1, value=splity1, inline=False)
            await ctx.send(embed=embed)
            embed2.add_field(name=title2, value=splity2, inline=False)
            await ctx.send(embed=embed2)

        if (len(outputList)) < 1000:
            embed.add_field(name=title, value=outputList, inline=False)
            await ctx.send(embed=embed)

    async def getlist(self, ctx):
        output = []
        for day in weekdays:
            list_of_anime = self.dict_of_anime.get(day, None)
            if list_of_anime:
                output.append('**[' + day + ']**')
                for item in list_of_anime:
                    output.append(item)
                
        await self.animeEmbedOutput(ctx, output, 'ANIME <:naneggu:564053655775346699>')

    @commands.command()
    @commands.has_role("anime")
    async def rebuild(self, ctx):
        if ctx.channel.id in channel_id:
            await ctx.send("Building anime tastes <:fatano:484069665212071936>")
            self.dict_of_anime = self.dict_builder()
            await ctx.send("Done i guess <:fatano:484069665212071936>")

    @commands.command()
    @commands.has_role("anime")
    async def anime(self, ctx):
        if ctx.channel.id in channel_id:
            await ctx.send("Anime @ PST")
            await self.getlist(ctx)

async def setup(bot):
    await bot.add_cog(animeCog(bot))
    print('anime cog loaded')


