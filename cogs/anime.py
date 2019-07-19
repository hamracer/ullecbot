import discord
from discord.ext import commands
from NyaaPy import Nyaa
import datetime
from collections import defaultdict
import requests
import json

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
today = datetime.datetime.today().strftime('%A')
user = None
msgr = None
thismessage = None
searchterm = None
counter = None
findcheck = None

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
            try:
                airing = (show['media']['nextAiringEpisode']['airingAt'])
                air_date = datetime.datetime.fromtimestamp(airing)
                output[weekdays[air_date.weekday()]].append(title)
            except:
                pass

            #  dictionary called output, inside list of weekdays, inside a list of days derived from the air_date

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

    @commands.command()
    @commands.has_role("anime")
    async def s(self, ctx, *args):
        if ctx.channel.id in channel_id:
            global searchterm
            searchterm = (" ".join(args[:]))
            # searchterm = searchterm + " horriblesubs 720"
            # if ctx.channel.id == "590798224764436499":
            global counter
            counter = 0
            display = self.anime_embed(searchterm, counter)
            global thismessage
            thismessage = await ctx.send(embed=display)
            if findcheck is True: 
                await thismessage.add_reaction(emoji=':best:579662404980572161')
                await thismessage.add_reaction(emoji=':worst:579662420537114626')
                global user
                global msgr
                user = ctx.message.author.id
                msgr = thismessage.id

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        global counter
        if payload.channel_id in channel_id:
            if payload.message_id == msgr:
                if payload.user_id == user:
                    if payload.emoji.id == 579662420537114626:
                        author = self.bot.get_user(user)
                        print("Match")
                        await thismessage.remove_reaction(self.bot.get_emoji(579662420537114626),author)
                        counter = counter + 1  
                        ndisplay = self.anime_embed(searchterm, counter)
                        await thismessage.edit(embed=ndisplay)

                    if payload.emoji.id == 579662404980572161:
                        author = self.bot.get_user(user)
                        print("Match")
                        await thismessage.remove_reaction(self.bot.get_emoji(579662420537114626),author)
                        counter = counter - 1  
                        if counter < 0: 
                            counter == 0
                        ndisplay = self.anime_embed(searchterm, counter)
                        await thismessage.edit(embed=ndisplay)
            else:
                print("payload does not match")


    def anime_embed(self, searchterm, i):     
        output=[]  
        pants = Nyaa.search(keyword=searchterm, category=1, subcategory=2)
        global findcheck     
        try:
            current = pants[i]
        except: 
            embed = discord.Embed(description="There are no results for "+searchterm)
            findcheck = False
            return embed
        name = current["name"]
        baddl = current["download_url"]
        dl = baddl.replace('http', 'https')
        output.append("**Search**: "+searchterm )
        output.append("**Title**: "+ name)
        output.append("**DL**: "+ " [link]("+ dl + ")")
        foutput = '\n'.join(output)
        embed = discord.Embed()
        v = i + 1
        nameterm = "Searching Nyaa, result: " + str(v)
        embed.add_field(name=nameterm, value=foutput, inline=False)
        findcheck = True
        return embed



def setup(bot):
    bot.add_cog(animeCog(bot))
    print('anime cog loaded')


