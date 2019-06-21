    
import discord
from discord.ext import tasks, commands
import json
import os

# approval URL for bot
# https://discordapp.com/oauth2/authorize?client_id=562335932813017134&scope=bot

bot = commands.Bot(command_prefix='.')  # bot command
coglist = ['admin', 'anime', 'help', 'snail']
bot.remove_command('help')

def loadconfig():
    # load globals defined in the config file

    global bot_token
    global channel_id

    try:
        with open('configs/config.json') as f:
            print('loading config file for main bot')
            data = json.load(f)
            channel_id = data['channel_id']
            try:
                bot_token = data['bot_token']
            except:
                bot_token = os.environ.get('bot_token')

        return True
    except Exception as e:
        print('Exception: ' + str(e))
        return False


if not loadconfig():
    exit()

# loading cogs
if __name__ == '__main__':
    for load in coglist:
        try:
            bot.load_extension('cogs.'+(load))
        except Exception as e:
            print('{} cannot be loaded. [{}]'.format(load, e))

# starting event
@bot.event
async def on_ready():
    print('Bot Running')

bot.run(bot_token)

