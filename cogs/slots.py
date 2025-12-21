import discord
from discord.ext import commands
import json
import random
import asyncio
import aiosqlite
import os

#emotes

#low tier
carlbig="<:carlbig:1452227219299504170>"
carlhat="<:carlhat:1452235034676301875>"
carlcone="<:carlcone:1452234506525216840>"
carlbrap="<:carlbrap:1452227236471246918>"
carlthumbsup="<:carlthumbsup:1452235456245665803>"


#high tier
carllick="<:carl_lick:1452227107395604574>"
carlsmuggy="<:carlsmuggy:1452234800038678541>"
carlpp="<:carlpp:1452226942827761765>"
carlpunch="<:carlpunch:1452235616975716474>"

#jackpot tier
carlchest="<:CarlChest:1452227128367255623>"
carldead="<:carldead:1452236017896521789>"

DB_PATH = '/opt/data/ullecbot/db/rolls.db' if os.path.exists('/opt/data/ullecbot/db') and os.access('/opt/data/ullecbot/db', os.W_OK) else 'db/rolls.db'

class DoubleOrNothingView(discord.ui.View):
    def __init__(self, user_id, amount, db_path, boss_kills):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.amount = amount
        self.db_path = db_path
        self.boss_kills = boss_kills

    @discord.ui.button(label="Double or Nothing", style=discord.ButtonStyle.green, emoji="🎲")
    async def double(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Not your spin!", ephemeral=True)
            return
        
        for child in self.children:
            child.disabled = True
        
        if random.random() < 0.5:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("UPDATE borpacoins SET amount = amount + ? WHERE user=?", (self.amount, self.user_id))
                await db.commit()
            await interaction.response.edit_message(content=interaction.message.content + f"\n\n**DOUBLED!** You won {self.amount * 2} Borpacoins! (Chance: 50%)", view=self)
        else:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("UPDATE borpacoins SET amount = amount - ? WHERE user=?", (self.amount, self.user_id))
                await db.commit()
            await interaction.response.edit_message(content=interaction.message.content + f"\n\n**LOST!** LMAO you lost it all. (Chance: 50%)", view=self)
        self.stop()

    @discord.ui.button(label="Cash Out", style=discord.ButtonStyle.grey)
    async def cash_out(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Not your spin!", ephemeral=True)
            return
        
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content=interaction.message.content + "\n\nCashed out safely.", view=self)
        self.stop()

class slotsCog(commands.Cog, name="slots"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="spin")
    async def spin(self, ctx):
        cost = 25
        
        # Check balance
        async with aiosqlite.connect(DB_PATH) as db:
            # Ensure table exists
            await db.execute("CREATE TABLE IF NOT EXISTS tokens (user INTEGER PRIMARY KEY, amount INTEGER)")
            await db.execute("CREATE TABLE IF NOT EXISTS borpacoins (user INTEGER PRIMARY KEY, amount INTEGER)")
            
            cursor = await db.execute("SELECT amount FROM tokens WHERE user=?", (ctx.author.id,))
            row = await cursor.fetchone()
            if not row or row[0] < cost:
                await ctx.reply(f"You don't have enough Tokens to play! (Cost: {cost})\nUse `/exchange` to get tokens.")
                return
            
            # Deduct cost
            await db.execute("UPDATE tokens SET amount = amount - ? WHERE user=?", (cost, ctx.author.id))
            
            # Get boss kills
            cursor = await db.execute("SELECT boss_kills FROM rolltable WHERE user=?", (ctx.author.id,))
            bk_row = await cursor.fetchone()
            boss_kills = bk_row[0] if bk_row else 0

            await db.commit()

        low_tier = [carlbig, carlhat, carlcone, carlbrap, carlthumbsup]
        high_tier = [carllick, carlsmuggy, carlpp, carlpunch]
        jackpot_tier = [carlchest, carldead]
        all_symbols = low_tier + high_tier + jackpot_tier

        ascii_header = "   ˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍ\n /                                 \\\n|   CARL MACHINE  |\n|=================|"
        ascii_footer = "|=================|\n \ \ˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍ /"

        msg = await ctx.reply("🎰 Spinning...")
        
        final_grid = []
        for i in range(5):
            grid = [[random.choice(all_symbols) for _ in range(5)] for _ in range(3)]
            grid_display = "\n".join(["| " + " ".join(row) + " |" for row in grid])
            await msg.edit(content=f"**SPINNING...**\n{ascii_header}\n{grid_display}\n{ascii_footer}")
            await asyncio.sleep(1)
            final_grid = grid

        total_payout = 0
        winnings_text = []

        paylines = [
            [1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [2, 2, 2, 2, 2], [0, 1, 2, 1, 0], [2, 1, 0, 1, 2],
            [0, 0, 1, 0, 0], [2, 2, 1, 2, 2], [1, 2, 2, 2, 1], [1, 0, 0, 0, 1], [0, 1, 1, 1, 0],
            [2, 1, 1, 1, 2], [0, 1, 0, 1, 0], [2, 1, 2, 1, 2], [1, 0, 1, 0, 1], [1, 2, 1, 2, 1],
            [1, 1, 0, 1, 1], [1, 1, 2, 1, 1], [0, 0, 2, 0, 0], [2, 2, 0, 2, 2], [0, 2, 2, 2, 0],
            [2, 0, 0, 0, 2], [0, 2, 0, 2, 0], [2, 0, 2, 0, 2], [0, 0, 1, 2, 2], [2, 2, 1, 0, 0]
        ]

        for line_idx, line in enumerate(paylines):
            symbols = [final_grid[line[i]][i] for i in range(5)]
            
            # Jackpot symbols act as wildcards
            check_symbol = next((s for s in symbols if s not in jackpot_tier), symbols[0])
            
            count = 0
            for symbol in symbols:
                if symbol == check_symbol or symbol in jackpot_tier:
                    count += 1
                else:
                    break
            
            if count >= 3:
                base_payout = 0
                if count == 3: base_payout = 1
                elif count == 4: base_payout = 5
                elif count == 5: base_payout = 25
                
                multiplier = 1
                if check_symbol in high_tier: multiplier = 2
                elif check_symbol in jackpot_tier: multiplier = 10
                
                win = base_payout * multiplier
                total_payout += win
                winnings_text.append(f"Line {line_idx+1}: {count}x {check_symbol} (+{win})")

        if total_payout > 0:
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("INSERT INTO borpacoins (user, amount) VALUES (?, ?) ON CONFLICT(user) DO UPDATE SET amount = amount + ?", (ctx.author.id, total_payout, total_payout))
                await db.commit()
            result_text = f"**WINNER!**\nMatches:\n" + "\n".join(winnings_text) + f"\n\nTotal Won: {total_payout} Borpacoins!"
        else:
            result_text = "No matches. Better luck next time!"

        final_display = "\n".join(["| " + " ".join(row) + " |" for row in final_grid])
        
        if total_payout > 0 and boss_kills >= 10:
            show_chance = 0.50 + ((boss_kills - 10) // 10) * 0.01
            if random.random() < show_chance:
                view = DoubleOrNothingView(ctx.author.id, total_payout, DB_PATH, boss_kills)
                await msg.edit(content=f"**RESULT**\n{ascii_header}\n{final_display}\n{ascii_footer}\n\n{result_text}\n\n**Double or Nothing?**", view=view)
            else:
                await msg.edit(content=f"**RESULT**\n{ascii_header}\n{final_display}\n{ascii_footer}\n\n{result_text}")
        else:
            await msg.edit(content=f"**RESULT**\n{ascii_header}\n{final_display}\n{ascii_footer}\n\n{result_text}")

        if total_payout == 0:
            await asyncio.sleep(5)
            await msg.delete()

    
async def setup(bot):
    await bot.add_cog(slotsCog(bot))
    print('slots cog loaded')