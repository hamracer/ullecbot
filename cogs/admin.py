import discord
from discord.ext import tasks, commands
import json
import re

pit = None
unpit = None
timer = 0
pitcount = 0
banlist = []

class adminCog(commands.Cog, name="admin"):

    def __init__(self, bot):
        self.bot = bot
        
    def loadconfig():
        global banlist
        global pit
        global timer
        global pitcount
        global unpit

        try:
            with open('configs/admin.json', 'r') as f:
                print('loading admin file for admin cog')
                data = json.load(f)
                banlist = data['banlist']
                pit = data['pit']
                timer = data["timer"]
                pitcount = data["pitcount"]
                unpit = data["unpit"]
            return True
        except Exception as e:
            print('Exception: ' + str(e))
            return False

    loadconfig()

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def pit(self, ctx):
        with open('configs/admin.json', 'r') as f:
            data = json.load(f)
        data['pit'] ^= True
        with open('configs/admin.json', 'w') as f:
            json.dump(data, f)
        if data['pit'] is True:
            # await ctx.send('Banlist is currently ON')
            await ctx.message.add_reaction(emoji=':best:579662404980572161')
        else:
            # await ctx.send('Banlist is currently OFF')
            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
        global pit
        pit = data['pit']

    @commands.command()
    async def banlist(self, ctx):
        with open('configs/admin.json', 'r') as f:
            data = json.load(f)
            currentbanlist = data['banlist']
            pit = data['pit']
        blist =[]
        for x in currentbanlist:
            blist.append(x)
        allblist = '\n'.join(blist)
        if pit is True:
            pitstats = "On"

        else:
            pitstats = "Off"
        await ctx.send("```md\n"
                       "# Banlist Phrases\n"
                       "Banlist is currently < {pitstats} >\n\n"
                       "{allblist}"
                       "\n```".format(allblist=allblist,pitstats=pitstats))

    @commands.command()
    @commands.has_role("the taihou champion")
    async def itadakms(self, ctx):
        await ctx.send("<:itadakms:567808973793656884><:itadakms:567808973793656884><:itadakms:567808973793656884>")
        await self.bot.logout()


    @commands.Cog.listener()
    async def on_message(self, message):  # pitting people by saying words in banned list
        channels = [339155308767215618]   # 585758519500865546
        if message.channel.id in channels:
            if pit is True:
                if message.author.id is self.bot.user.id:
                    return
                else:
                    mess = message.content
                    for words in banlist:
                        my_regex = r"(^|\s|[^:a-zA-Z])" + re.escape(words) + r"(\s|[^:a-zA-Z]|$)"
                        if re.search(my_regex, mess, re.IGNORECASE):
                            with open('configs/admin.json', 'r') as f:
                                data = json.load(f)
                                global pitcount
                                pitcount = data['pitcount']
                            pitcount += 1
                            user = message.author
                            role = discord.utils.get(message.guild.roles, name='you brought this onto yourself')
                            await message.channel.send(f'{user} has been pitted for kill number {pitcount} <:umagun:579673776929636352>')
                            await user.add_roles(role)
                            with open('configs/admin.json', 'w') as f:
                                data['pitcount'] = pitcount
                                json.dump(data, f)
                            return


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unpit(self, ctx):
        with open('configs/admin.json', 'r') as f:
            data = json.load(f)
            global unpit
            unpit = data['unpit']
        unpit ^= True
        if unpit is True:
            await ctx.message.add_reaction(emoji=':best:579662404980572161')
            self.unpitter.start(ctx)
        else:
            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
            self.unpitter.cancel()
        with open('configs/admin.json', 'w') as f:
            data['unpit'] = unpit
            json.dump(data, f)
        

    @commands.Cog.listener()
    async def on_ready(self):
        ctx = self.bot.get_channel(339155308767215618)
        if unpit is True:
            self.unpitter.start(ctx)
        else:
            self.unpitter.cancel()


    @tasks.loop(seconds=timer)
    async def unpitter(self, ctx):
        try:
            role = discord.utils.get(ctx.message.guild.roles, name='you brought this onto yourself')
            for member in ctx.message.guild.members:
                if role in member.roles:
                    await member.remove_roles(role)
        except:
            guild = self.bot.get_guild(339155308767215618)
            role = discord.utils.get(guild.roles, name='you brought this onto yourself')
        for member in guild.members:
            if role in member.roles:
                await member.remove_roles(role)


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def timer(self, ctx, arg):
        with open('configs/admin.json', 'r') as f:
            data = json.load(f)
            global timer
            timer = data['timer']
        try:
            arg = int(arg)
        except:
            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
            return
        timer = arg
        if timer < 1:
            timer = 600
            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
            self.unpitter.change_interval(seconds=timer)
        else:
            await ctx.message.add_reaction(emoji=':best:579662404980572161')
            self.unpitter.change_interval(seconds=timer)
        with open('configs/admin.json', 'w') as f:
            data['timer'] = timer
            json.dump(data, f)



    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def banadd(self, ctx, *args):
        newban = (" ".join(args[:]))
        with open('configs/admin.json', 'r') as f:
            data = json.load(f)
            global banlist
            banlist = data['banlist']
        if newban in banlist:
            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
        else:
            banlist.append(newban)
            await ctx.message.add_reaction(emoji=':best:579662404980572161')
            with open('configs/admin.json', 'w') as f:
                data['banlist'] = banlist
                json.dump(data, f)


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def banremove(self, ctx, *args):
        oldban = (" ".join(args[:]))
        with open('configs/admin.json', 'r') as f:
            data = json.load(f)
            global banlist
            banlist = data['banlist']
        if oldban not in banlist:
            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
        else:
            banlist.remove(oldban)
            await ctx.message.add_reaction(emoji=':best:579662404980572161')
            with open('configs/admin.json', 'w') as f:
                data['banlist'] = banlist
                json.dump(data, f)

    @commands.command()
    async def status(self, ctx):
        with open('configs/admin.json', 'r') as f:
            data = json.load(f)
            if data['pit'] is True:
                pitstat = 'on'
            else:
                pitstat = 'off'
            if unpit is True:
                unpitstat = 'on'
            else:
                unpitstat = 'off'

            string = (f"```md\n"
                           f"# Function Status\n\n"
                           f"Pit is < {pitstat} >\n"
                           f"Unpit is < {unpitstat} >\n"
                           f"Unpit is at < {timer} >\n"
                           f"```")
            await ctx.send(string)


def setup(bot):
    bot.add_cog(adminCog(bot))
    print('admin cog loaded')

