import discord
from discord.ext import tasks, commands
from discord.ext.commands import CommandNotFound, MissingPermissions
import json
import os


# approval URL for bot
# https://discordapp.com/oauth2/authorize?client_id=562335932813017134&scope=bot

bot = commands.Bot(command_prefix='.')  # bot command
coglist = ['help', 'starchart']
# coglist = ['modabuse', 'snail', 'admin', 'help', 'starchart', 'dice']
bot.remove_command('help')

def loadtoken():
    # load globals defined in the config file

    global bot_token

    try:
        with open('configs/token.json') as f:
            print('loading token file for main bot')
            data = json.load(f)
            try:
                bot_token = data['bot_token']
            except:
                bot_token = os.environ.get('bot_token')
        return True

    except Exception as e:
        print('Exception: ' + str(e))
        return False

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
            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
            return
        
        if isinstance(error, CommandNotFound):
            await ctx.message.add_reaction(emoji=':worst:579662420537114626')
            return
        raise error

# starting event
@bot.event
async def on_ready():
    print('Bot Running')

bot.run(bot_token)



