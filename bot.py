import discord
from discord.ext import tasks, commands
from discord.ext.commands import CommandNotFound, MissingPermissions
import json
import os
import random


# approval URL for bot
# https://discordapp.com/oauth2/authorize?client_id=562335932813017134&scope=bot

bot = commands.Bot(command_prefix='.')  # bot command
#'snail', 'admin', 'help', 'starchart', 'dice', 'echo', 'pingstats', 'anime','dnd','uwu'
coglist = ['snail', 'help', 'dice', 'echo', 'pingstats', 'anime','dnd','uwu']
bot.remove_command('help')
spook = [   "This only makes me stronger.",
            "I’m /gbfg/'s reckoning.",
            "GIVE ME MORE",
            "Welcome to the future.",
            "Did you think that I'd forget?",
            "SHHHHHHHHHAAAAAAAAAAAAAARK",
            "I am inevitable."
            ]
def loadtoken():
    # load globals defined in the config file

    global bot_token

    try:
        with open('configs/token.json') as f:
            print('loading token file for main bot')
            data = json.load(f)
            bot_token = data['bot_token']
            return True
    except:
        bot_token = os.environ.get('bot_token')
        return True



if not loadtoken():
    exit()

# loading cogs
if __name__ == '__main__':
    for load in coglist:
        try:   
            bot.load_extension('cogs.'+(load))
        except Exception as e:
            print('{} cannot be loaded. [{}]'.format(load, e))

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.message.add_reaction(emoji='😏')
            if random.randint(1,100) <= 30:
                await ctx.send(spook[random.randint(0,6)])
            return

        raise error

# starting event
@bot.event
async def on_ready():
    print('Bot Running')

bot.run(bot_token)



