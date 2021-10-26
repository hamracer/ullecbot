import discord
from discord.ext import commands, tasks
import json, random
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

gbfgid = '339155308767215618'
borpaspin = '<a:borpaspin:897668937926451210>'
plusone = '<:plusone:899989682555854868>'
loading = '<a:loading:902407104499974144>'
tick = '<:tick:902416135683702794>'


enders = []

def gspreadload():

    try:
        gc = gspread.service_account(filename='configs/blissful-land-240720-c3abbb49b748.json')

    except:
        scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
        json_creds = os.environ.get('gspread_creds')
        creds_dict = json.loads(json_creds)
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
        gc = gspread.authorize(creds)
        
    return gc


def readfromsheet():
    
    #print('readfromsheet')
    gc = gspreadload()
    #start from scratch
    global enders
    enders = []
    worksheet = gc.open('botstuff').get_worksheet(1)
    username_spread = worksheet.col_values(2)
    rolls_spread  = worksheet.col_values(3)
    players = [list(a) for a in zip(username_spread, rolls_spread )]
    cats = ["username", "rolls"]
    
    for i in players:
        new = dict(zip(cats, i))
        enders.append(new)
    #print("players: " + str(players))
    #print("readfromsheet - end")
    return enders


def writetosheet(enders):

    #print('writetosheet')
    gc = gspreadload()


    ll = len(enders)
    end = "C" + str(ll)
    listy = []
    for i in enders:
        for o in i.values():
            listy.append(o)
    x = 2
    newlisty = [listy[i:i+x] for i in range (0, len(listy), x)]
    #print("listy: " + str(listy))
    #print("newlisty:" + str(newlisty))
    #print("end: "+ str(end))
    worksheet = gc.open('botstuff').get_worksheet(1)
    worksheet.update('B1:'+ end ,newlisty)
    #print("writetosheet - end")
    return

def rolling(test=False):
    
    if test is False:
        theroll = random.randint(1,100)
    else: 
        theroll = int(test)

    if theroll > 99:
        roll = "https://cdn.discordapp.com/attachments/262371002577715201/875547855648079872/unknown.png"
        return roll
    if theroll >= 94:
        roll = borpaspin
        return roll
    else:
        roll = "cum"
        return roll
    
    

class echoCog(commands.Cog, name="echo"):
    def __init__(self, bot):
        self.bot = bot
        self.cummies.start()
        global logchannel
        
        

    def loadgatcha():
        global enders
        enders = readfromsheet()

    loadgatcha()

    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def testroll(self, ctx, arg):
        roll = rolling(arg)
        await ctx.reply(roll)


    @commands.command()
    async def cum(self, ctx):
        if str(ctx.channel.id) == '262371002577715201' or '562352225423458326':
            await ctx.message.add_reaction(emoji=loading) 
            
            #print("CUMMMMMMMMMMMMMMMMMMMMMMM")
            global enders
            #print("enders: " + str(enders))
            playername = ctx.author.name
            if any(i['username'] == playername for i in enders):
                print("player exists: " + str(playername))
            else:
                #print("player doesn't exists")
                enders.append({"username":playername,"rolls":4})
                #print(enders)
                writetosheet(enders)
        #check if user has enough rolls to roll
        enders = readfromsheet()  
        match = next((item for item in enders if item['username'] == playername), 'Nothing Found')
        if int(match['rolls']) > 0:
            match['rolls'] = int(match['rolls']) - 1
            roll = rolling()
            writetosheet(enders)
            await ctx.reply(roll)
            await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
            await ctx.message.add_reaction(emoji=tick) 
        else: 
            await ctx.reply("u got no cums loser")
            await ctx.message.remove_reaction(emoji=loading, member=self.bot.get_user(562335932813017134)) 
            await ctx.message.add_reaction(emoji=tick) 

    @commands.command()
    async def cumboard(self, ctx):
        if str(ctx.channel.id) == '262371002577715201' or '562352225423458326':
            enders.sort(key=lambda x:x['rolls'], reverse=True)
            displaycumboard = [("%s with %s cums"%(item['username'], item['rolls'])) for item in enders[0:5]]
            sep = '\n'
            await ctx.send("Top 5 Cummers:\n" + sep.join(displaycumboard))

                



    @commands.command()
    async def howmanycumsdoihaveleft(self, ctx):
        if str(ctx.channel.id) == '262371002577715201' or '562352225423458326':
            playername = ctx.author.name
            try:
                match = next((item for item in enders if item['username'] == playername), 'Nothing Found') 
                await ctx.reply("You have " + str(match['rolls']) + " cums left.")
            except:
                await ctx.reply("You're not on the cummies list, please cum once first.")

    @tasks.loop(hours=1)
    async def cummies(self):
        enders = readfromsheet()
        for i in enders:
            i['rolls'] = int(i['rolls']) + 1
        writetosheet(enders)

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.id) == '262371002577715201':
            textroll = random.randint(1,1000)
            if textroll  >= 970:
                playername = message.author.name
                try:
                    match = next((item for item in enders if item['username'] == playername), 'Nothing Found')
                    match['rolls'] = int(match['rolls']) + 1
                    await message.add_reaction(emoji=plusone) 
                    writetosheet(enders)
                    channel = self.bot.get_channel(902418660767965184)
                    await channel.send(playername + " rolled: " + textroll)
                except:
                    print('no user')


def setup(bot):
    bot.add_cog(echoCog(bot))
    print('echo cog loaded')

