from discord.ext import commands
import tweepy, json
import os

gbfgid = '339155308767215618'

class dumpCog(commands.Cog, name="dump"):
    def __init__(self, bot):
        self.bot = bot


    def loadconfig():
        global CONSUMER_KEY
        global CONSUMER_SECRET
        global OAUTH_TOKEN
        global OAUTH_TOKEN_SECRET

        try:
            with open('configs/twitter.json', 'r') as f:
                print('twitter for echo cog')
                data = json.load(f)
                CONSUMER_KEY = data['CONSUMER_KEY']
                CONSUMER_SECRET = data['CONSUMER_SECRET']
                OAUTH_TOKEN = data['OAUTH_TOKEN']
                OAUTH_TOKEN_SECRET = data['OAUTH_TOKEN_SECRET']

            return True
        except:
            
            CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
            CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
            OAUTH_TOKEN = os.environ.get('OAUTH_TOKEN')
            OAUTH_TOKEN_SECRET = os.environ.get('OAUTH_TOKEN_SECRET')

            return True

    loadconfig()
    


    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.id) == '599327014146539520':
            gbfg = self.bot.get_channel(int(gbfgid))
            await gbfg.send(message.content) 
          


    @commands.command()
    async def howmanydaysuntilendwalker(self, ctx):
        auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
        auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        api = tweepy.API(auth)
        username="DaysUntilEW"
        tweetlist = api.user_timeline(id=username ,count=1)
        latest = tweetlist[0]
        post = "https://twitter.com/DaysUntilEW/status/" + str(latest.id)
        await ctx.send(post)



def setup(bot):
    bot.add_cog(dumpCog(bot))
    print('dump cog loaded')

