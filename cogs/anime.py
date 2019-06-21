import discord
from discord.ext import commands
from NyaaPy import Nyaa
import datetime
from collections import defaultdict
import requests
import json

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
today = datetime.datetime.today().strftime('%A')


class animeCog(commands.Cog, name="anime"):
    dict_of_anime = None

    def __init__(self, bot):
        self.bot = bot

        if not self.dict_of_anime:
            print('bulding anime shit')
            self.dict_of_anime = self.dict_builder()


    def loadreplace():
        global replacelist

        try:
            with open('configs/replacelist.json') as f:
                print('loading replace list')
                data = json.load(f)
                replacelist = data['replacelist']
            return True
        except Exception as e:
            print('Exception: ' + str(e))
            return False

    def loadconfig():
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

    loadconfig()
    loadreplace()

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

        for show in data['data']['MediaListCollection']['lists'][0]['entries']:
            title = (show['media']['title']['romaji'])
            airing = (show['media']['nextAiringEpisode']['airingAt'])

            air_date = datetime.datetime.fromtimestamp(airing)
            output[weekdays[air_date.weekday()]].append(title)


        return output


    async def get_weekday_anime(self, ctx, day):
        list_of_anime = self.dict_of_anime.get(day, None)
        output = []
        if list_of_anime:
            output.append('**[' + day + ']** \n')
            for item in list_of_anime:
                async with ctx.typing():
                    for a in replacelist:
                        for i in list_of_anime:
                            if a['Title'] == i:
                                term = item.replace(a['Title'], a['Replace'])  # some titles dont work replace here
                                break
                            else:
                                term = item
                    search = term + " horriblesubs 720"
                    pants = Nyaa.search(keyword=search, category=1, subcategory=2)
                    latest = pants[0]
                    torrentname = latest["name"]
                    animelink = latest["download_url"]
                    newanimelink = animelink.replace('http', 'https')  # replace http with https
                    output.append("**" + item + "**")
                    output.append(torrentname + " [link]("+ newanimelink + ")")

        mess = '\n'.join(output)
        embed = discord.Embed()
        embed.add_field(name='Anime time <:naneggu:564053655775346699>', value=mess, inline=False)
        await ctx.send(embed=embed)


    async def getlist(self, ctx):
        output = []
        for day in weekdays:
            list_of_anime = self.dict_of_anime.get(day, None)
            if list_of_anime:
                output.append('**[' + day + ']** \n')
                for item in list_of_anime:
                    output.append(item)
                output.append('\n')
        mess = '\n'.join(output)
        embedlist = discord.Embed()
        embedlist.add_field(name='Heres a list <:naneggu:564053655775346699>', value=mess, inline=False)
        await ctx.send(embed=embedlist)



    @commands.command()
    @commands.has_role("anime")
    async def chen(self, ctx, day=today):
        if ctx.channel.id in channel_id:
            day = day.capitalize()
            if day in weekdays:
                await ctx.send("Give me some time <:naneugg:564051785673867313>")
                await self.get_weekday_anime(ctx, day)
            if day == "Yesterday":
                yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%A')
                day = yesterday
                await ctx.send("Give me some time <:naneugg:564051785673867313>")
                await self.get_weekday_anime(ctx, day)


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
            await ctx.send("This is what we're watching this season <:haneeh:567548762843512832>")
            await self.getlist(ctx)


def setup(bot):
    bot.add_cog(animeCog(bot))
    print('anime cog loaded')


