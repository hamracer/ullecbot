import discord
from discord.ext import tasks, commands
from discord.ext.commands import CommandNotFound, MissingPermissions
import json
import os
import random
import asyncio


# approval URL for bot
# https://discordapp.com/oauth2/authorize?client_id=562335932813017134&scope=bot

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.', intents=intents)  # bot command

#coglist = ['anime','fx','apex']
coglist = ['pit2']

bot.remove_command('help')

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
async def load():
    for cogs in coglist:
        try:
            await bot.load_extension('cogs.'+(cogs))
        except Exception as e:
            print('{} cannot be loaded. [{}]'.format(load, e))
    
    #for filename in os.listdir('./cogs'):
    #    if filename.endswith('.py'):
    #        await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.command()
async def rcl(ctx):
    for cogs in coglist:
        try:
            await bot.reload_extension('cogs.'+(cogs))
        except Exception as e:
            print('{} cannot be reloaded. [{}]'.format(load, e))

async def main():
    await load()
    await bot.start(bot_token)

90
# starting event
@bot.event
async def on_ready():
    print('Bot Running')

asyncio.run(main())
