import discord
from discord.ext import commands


class helpCog(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        author = ctx.message.author
        helpmessage =[]
        helpmessage.append("```md")

        helpmessage.append("# How to use ellec-bot")
        helpmessage.append("\n")
        helpmessage.append("< Anime Functions >")
        helpmessage.append("<anime functions only for 'anime' role and in #eye-cartons>")
        helpmessage.append("anime - list of anime we're watching this season")
        helpmessage.append("chen *- anime for that day with links")
        helpmessage.append("        * defaults today"
                           "        * yesterday"
                           "        * day (eg. Friday)")
        helpmessage.append("rebuild - rebuild the anime cache")
        helpmessage.append("\n")

        helpmessage.append('< Admin Functions >')
        helpmessage.append('banlist - list of banned words/phrases')
        helpmessage.append('status - list of current function statuses')
        modrole = discord.utils.get(ctx.guild.roles, name="mod")
        if modrole in author.roles:
            helpmessage.append('pit - toggles pit function')
            helpmessage.append('unpit - toggles an unpit function')
            helpmessage.append('timer * - change the time on unpit after the next unpit')
            helpmessage.append('banadd * - add a term to the banlist')
            helpmessage.append('banremove * - removes a term from the banlist')
        helpmessage.append("```")
        mess = '\n'.join(helpmessage)
        await author.send(mess)

    @commands.command()
    async def print(self, ctx, arg):
        print(arg)

    @commands.command()
    async def m(self, ctx):
        for i in ctx.message.embeds:
            print("field")
            print(i.author)
            print(i.title)
            print(i.url)
            print(i.description)
            print(i.fields)
            print(i.image)

    @commands.command()
    async def e(self, ctx):
        if ctx.message.embeds == True:
            print("Hello")
 

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def pitroulette(self, ctx):
        await ctx.send("%pitroulette")


    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters.
        Only up to 25 characters at a time.
        """

        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'
        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send('Output too long to display.')
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(helpCog(bot))
    print('help cog loaded')