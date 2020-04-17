import discord
from discord.ext import commands
from NyaaPy import Nyaa
import datetime
from collections import defaultdict
import requests
import json
import pytz


weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
today = datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).strftime('%A')

user = None
msgr = None
thismessage = None
searchterm = None
counter = None
findcheck = None
replacelist = None
channel_id = None
server_id = None

class animeCog(commands.Cog, name="anime"):
    dict_of_anime = None

    searchOptions = ["horriblesubs 720", "judas", "PAS"]

    def __init__(self, bot):
        self.bot = bot

        if not self.dict_of_anime:
            print('bulding anime shit')
            self.dict_of_anime = self.dict_builder()

        self.loadconfig()
        self.loadreplace()

    async def searchNyaa(self, animeName, term):
        search = " ".join([animeName, term])
        searchOutput = Nyaa.search(keyword=search, category=1, subcategory=2)
        latest = searchOutput[0]
        torrentName = latest["name"]
        animelink = latest["download_url"]
        newAnimeLink = animelink.replace('http://', 'https://')  # replace http with https
        return torrentName, newAnimeLink
    
    def loadreplace(self):
        global replacelist

        try:
            with open('configs/replacelist.json', encoding='utf-8') as f:
                print('loading replace list')
                data = json.load(f)
                replacelist = data['replacelist']
            return True
        except Exception as e:
            print('Exception: ' + str(e))
            return False

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

        for show in data['data']['MediaListCollection']['lists'][0]['entries']:
            title = (show['media']['title']['romaji'])
            try:
                airing = (show['media']['nextAiringEpisode']['airingAt'])
                air_date = (datetime.datetime.fromtimestamp(airing) - datetime.timedelta(hours=10))
                output[weekdays[air_date.weekday()]].append(title)
            except:
                pass

            #  dictionary called output, inside list of weekdays, inside a list of days derived from the air_date

        return output


    async def get_weekday_anime(self, ctx, day):
        list_of_anime = self.dict_of_anime.get(day, None)
        output = []
        output1 = []
        output2 = []
        if list_of_anime:
            output.append('**[' + datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).strftime('%a, %H:%M:%S') + " JST" + ']** \n')
            for item in list_of_anime:
                async with ctx.typing():
                    for anime in list_of_anime:
                        for replacer in replacelist:
                            title = replacer['Title']
                            newtitle = replacer['Replace']
                            if title == anime:
                                term = item.replace(title, newtitle)
                                break
                            else:
                                term = item

                    # use iteration instead of a billion tries
                    for searchTerm in self.searchOptions:
                        foundSwitch = False
                        print(searchTerm)
                        try:
                            torrentName, torrentLink = await self.searchNyaa(term, searchTerm)
                            if output:
                                foundSwitch = True
                                output.append("**" + item + "**")
                                output.append(torrentName + " [link]("+ torrentLink + ")")
                                break
                        except:
                            pass
                    if not foundSwitch:
                        print("issue, couldn't find anime: " + term)
                        output.append("Something went wrong <:naneugg:564051785673867313>")

        totalEmbedsPages = len(output) / 9
        
        for x in range(totalEmbedsPages+1):
            if x == 0:
                embedField = 'Anime time <:naneggu:564053655775346699>'
            else:
                embedField = 'More Anime time <:naneggu:564053655775346699>'
            sliceObject = output[x*9:(x+1)*9]
            await self.animeEmbedOutput(ctx, sliceObject, embedField)

    async def animeEmbedOutput(self, ctx, listSlice, title):
        outputList = '\n'.join(listSlice)
        embed = discord.Embed()
        print(len(outputList))
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

        await self.animeEmbedOutput(ctx, output, 'Heres a list <:naneggu:564053655775346699>')


    @commands.command()
    @commands.has_role("anime")
    async def chen(self, ctx, day=today):
        if ctx.channel.id in channel_id:
            day = day.capitalize()
            if day in weekdays:
                await ctx.send("Give me some time <:naneugg:564051785673867313>")
                await self.get_weekday_anime(ctx, day)
            if day == "Yesterday":
                yesterday = (datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')) - datetime.timedelta(days=1)).strftime('%A')
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
            global counter
            counter = 0
            async with ctx.typing():
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
                        await thismessage.remove_reaction(self.bot.get_emoji(579662404980572161),author)
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


