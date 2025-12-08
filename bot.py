import discord
from discord import app_commands
from discord.ext import tasks, commands
import json
import os
import random
import asyncio
import sys
import glob

# approval URL for bot
# https://discordapp.com/oauth2/authorize?client_id=562335932813017134&scope=bot

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.', intents=intents)  # bot command
coglist = [os.path.basename(f)[:-3] for f in glob.glob("cogs/[!_]*.py")]
bot.remove_command('help')

def loadtoken():
    # load globals defined in the config file

    global bot_token

    if sys.platform == 'win32':
        print('real win32 pog')
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
    print(f"Loading cogs: {coglist}")  # Debug to see what's being loaded
    
    for cog in coglist:
        try:
            await bot.load_extension('cogs.' + cog)
            print(f'{cog} loaded successfully')
        except Exception as e:
            print(f'{cog} cannot be loaded. [{e}]')

    MY_GUILD = discord.Object(id=562352224840187917)  # optional: limits visibility to this guild

    @bot.tree.command(name="re", description="Reload all cogs (owner only)", guild=MY_GUILD)
    async def re_reload(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        results = []
        for cog in coglist:
            try:
                await bot.reload_extension('cogs.' + cog)
                results.append(f"✅ {cog}")
            except Exception as e:
                results.append(f"❌ {cog}: {e!r}")
        await interaction.followup.send("Reload results:\n" + "\n".join(results), ephemeral=True)

    @bot.tree.command(name="ssync", description="Sync slash commands to the guild (owner only)", guild=MY_GUILD)
    @app_commands.describe(guildid="Guild ID to sync to (optional)")
    async def ssync(interaction: discord.Interaction, guildid: str = None):
        # owner check
        if not await bot.is_owner(interaction.user):
            await interaction.response.send_message("Only the bot owner can use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # resolve target guild
        try:
            target_id = int(guildid) if guildid else MY_GUILD.id
        except Exception:
            await interaction.followup.send("Invalid guild id provided.", ephemeral=True)
            return

        guild_obj = discord.Object(id=target_id)
        try:
            bot.tree.copy_global_to(guild=guild_obj)
            synced = await bot.tree.sync(guild=guild_obj)
            await interaction.followup.send(f"Synced {len(synced)} commands to guild {guild_obj.id}.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Sync failed: {e}", ephemeral=True)
            print("ssync error:", repr(e))




@bot.command()
@commands.is_owner()
async def itadakimas(ctx):
    await ctx.bot.logout()

async def main():
    await load()
    await bot.start(bot_token)

# starting event
@bot.event
async def on_ready():
    print('Bot Running')

    # sync app commands once the client has an application_id (run once)
    if not getattr(bot, "_app_commands_synced", False):
        try:
            MY_GUILD = discord.Object(id=562352224840187917)
            bot.tree.copy_global_to(guild=MY_GUILD)
            await bot.tree.sync(guild=MY_GUILD)
            bot._app_commands_synced = True
            print("App commands synced to guild", MY_GUILD.id)
        except Exception as e:
            print("Failed to sync app commands on_ready:", repr(e))

asyncio.run(main())
