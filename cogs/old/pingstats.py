import discord
from discord.ext import commands
import re
import operator
import collections

class pingstatsCog(commands.Cog, name="pingstats"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def emptyrole(self, ctx):

        guildroles=[]
        grlist=[]
        userrole={}

        guildroles = ctx.guild.roles
        for i in guildroles:
            grlist.append(i.name)
        for members in ctx.guild.members:
            for roles in members.roles:
                role = roles.name
                
                try:
                    userrole[role] = userrole[role] + 1
                except:
                    userrole[role] = 1

        roleset = set(userrole)
        serverset = set(grlist)
        result = (list(serverset - roleset))
        result = '\n'.join(result)
        embed=discord.Embed(title="Roles with no members:", description=result)
        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def rolenum(self, ctx, arg):

        guildroles=[]
        grlist=[]
        userrole={}
        result=[]

        guildroles = ctx.guild.roles
        for i in guildroles:
            grlist.append(i.name)
        for members in ctx.guild.members:
            for roles in members.roles:
                role = roles.name
                try:
                    userrole[role] = userrole[role] + 1
                except:
                    userrole[role] = 1
        for i in userrole:
            if userrole[i] == int(arg):
                result.append(i)
            else:
                pass
        result = '\n'.join(result)
        embed=discord.Embed(title="Roles with " + arg + " members:", description=result)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def roleping(self, ctx):
        channel = ctx.channel
        output = []
        nlist = {}
        nnlist = {}
        di = {}
        my_regex = r"(<@&)[0-9]+(>)"
        await ctx.send("Checking the last 1000 messages...")
        
        async for message in channel.history(limit=1000):
            term = re.search(my_regex, message.content)
            if term is not None:
                bingo = term[0]
                try:
                    di[bingo] = di[bingo] + 1
                except:
                    di[bingo] = 1

        for id, i in enumerate(di):
            key = list(di)[id]
            key = key.strip("<@&")
            key = key.strip(">")
            role = ctx.guild.get_role(int(key))
            rolename = role.name
            v = di.get(i)
            nlist[rolename] = v

        sorted_x = sorted(nlist.items(), reverse=True, key=operator.itemgetter(1))
        sorted_nlist = collections.OrderedDict(sorted_x)

        for k, v in sorted_nlist.items():
            output.append(k+": "+str(v))
        result = '\n'.join(output)
        embed=discord.Embed(title="Roles sorted by number of pings: ", description=result)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def userping(self, ctx):
        channel = ctx.channel
        output = []
        nlist = {}
        di = {}
        my_regex = r"(<@)[0-9]+(>)"
        await ctx.send("Checking the last 1000 messages...")
        
        async for message in channel.history(limit=1000):
            term = re.search(my_regex, message.content)
            if term is not None:
                bingo = term[0]
                try:
                    di[bingo] = di[bingo] + 1
                except:
                    di[bingo] = 1

        for id, i in enumerate(di):
            key = list(di)[id]
            key = key.strip("<@")
            key = key.strip(">")
            user = self.bot.get_user(int(key))
            username = user.name
            v = di.get(i)
            nlist[username] = v

        sorted_x = sorted(nlist.items(),reverse=True,key=operator.itemgetter(1))
        sorted_nlist = collections.OrderedDict(sorted_x)

        for k, v in sorted_nlist.items():
            output.append(k+": "+str(v))
        result = '\n'.join(output)
        embed=discord.Embed(title="Users sorted by number of pings: ", description=result)
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(pingstatsCog(bot))
    print('pingstats cog loaded')
