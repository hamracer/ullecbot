import discord
from discord import app_commands
from discord.ext import commands
import json
import re
import aiohttp

class stealsCog(commands.Cog, name="steals"):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="steal",
            callback=self.steal,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    async def steal(self, interaction: discord.Interaction, message: discord.Message):
        if message.stickers:
            await interaction.response.send_message(message.stickers[0].url, ephemeral=True)
            return

        custom_emojis = re.findall(r'<a?:[a-zA-Z0-9\_]+:[0-9]+>', message.content)
        if custom_emojis:
            emoji = discord.PartialEmoji.from_str(custom_emojis[0])
            await interaction.response.send_message(emoji.url, ephemeral=True)

            target_guild_id = 562352224840187917
            guild = self.bot.get_guild(target_guild_id)

            if not guild:
                await interaction.followup.send("Could not find the target guild to add the emoji to.", ephemeral=True)
                return

            if not guild.me.guild_permissions.manage_emojis_and_stickers:
                await interaction.followup.send(f"I don't have permission to add emojis in {guild.name}.", ephemeral=True)
                return

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(emoji.url) as resp:
                        if resp.status != 200:
                            await interaction.followup.send("Failed to download emoji image.", ephemeral=True)
                            return
                        image_bytes = await resp.read()
                new_emoji = await guild.create_custom_emoji(name=emoji.name, image=image_bytes, reason=f"Stolen by {interaction.user}")
                await interaction.followup.send(f"Successfully added {new_emoji} to {guild.name}!", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.followup.send(f"Failed to add emoji: {e}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"An unexpected error occurred: {e!r}", ephemeral=True)
            return

        await interaction.response.send_message("No stealable content found!", ephemeral=True)



    
async def setup(bot):
    await bot.add_cog(stealsCog(bot))
    print('steals cog loaded')