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


def setup(bot):
    bot.add_cog(helpCog(bot))
    print('help cog loaded')