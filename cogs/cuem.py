import discord
from discord.ext import commands
import json
import datetime
import random
import asyncio
import aiosqlite


#active channel list
channel_id=[1446500430954631359,1447552037100453909]

#emoji list
loading = '<a:loading:902407104499974144>'
borpaspin = '<a:borpaspin:905835451204640829>'
goldborpaspin = '<a:goldborpaspin:906324859007696916>'
rainbowborpaspin = '<a:rainbowborpaspin:1447183660640894996>'
borpa = '<:borpa:1446834792934015089>'
ldash = '<:ldash:727000991097946112>'
blank = '<:blank:525377105308024853>'
mpreg = '<:mpregful:1409028460667605154>'
cum = '<a:CUM:1446834290989203619>'


async def rolling():
    print("rolling")
    r1=random.randint(1,100)
    print(r1)
    if r1>50:
        roll=borpaspin
        r2=random.randint(1,100)
        print(r2)
        if r2>50:
            roll=borpaspin
            r3=random.randint(1,100)
            print(r3)
            if r3>50:
                roll=goldborpaspin
    else:
        roll=borpa
    print(roll)
    return roll
    

class cuemCog(commands.Cog, name="cuem"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(2, 60, commands.BucketType.user)
    #@commands.is_owner()
    async def cum2(self, ctx):
        """Usage: .cum2 -> opens the in-channel borpa selection menu (only you can interact)"""
        if ctx.channel.id not in channel_id:
            return

        playerid = ctx.author.id

        # Helper to apply damage to the mpreg boss (updates configs/mpreg_hp.json)
        async def apply_damage(amount: int, user_id: int = None, roll_type: str = None):
            def _sync_apply():
                path = 'configs/mpreg_hp.json'
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception:
                    data = {"name": "mpreg", "hp": 100000, "max_hp": 100000}
                try:
                    data['old_hp'] = int(data.get('hp', 0))
                    hp = int(data.get('hp', 0))
                except Exception:
                    hp = 0

                boss_killed = (hp - int(amount)) <= 0
                hp = max(0, hp - int(amount))

                if boss_killed and hp == 0:
                    data['hp'] = data.get('max_hp', 100000) # Reset to max HP
                else:
                    data['hp'] = hp

                data['last_updated'] = datetime.datetime.utcnow().isoformat() + 'Z'
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                except Exception:
                    pass
                return data, boss_killed  # Return boss_killed status

            # update JSON on disk in thread
            boss_data, boss_was_killed = await asyncio.to_thread(_sync_apply)

            # also log the damage into rolls.db
            try:
                async with aiosqlite.connect('rolls.db') as db:
                    await db.execute('''
                        CREATE TABLE IF NOT EXISTS boss_damage (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user INTEGER,
                            damage INTEGER,
                            roll_type TEXT,
                            ts TEXT
                        )
                    ''')
                    ts = datetime.datetime.utcnow().isoformat() + 'Z'
                    await db.execute('INSERT INTO boss_damage (user, damage, roll_type, ts) VALUES (?,?,?,?)', [user_id, int(amount), roll_type, ts])
                    await db.commit()
                    # If boss was killed, increment boss_kills for the user
                    if boss_was_killed:  # Use the new flag
                        print(f"Boss killed by {user_id}. Incrementing boss_kills.")
                        await db.execute("UPDATE rolltable SET boss_kills = boss_kills + 1 WHERE user = ?", [user_id])
                        await db.commit()
            except Exception:
                # non-fatal logging failure
                pass

            # Return both the boss data and the kill status
            return boss_data, boss_was_killed

            # Helper to run the existing animation given a resolved roll and dmg info
        async def do_animation(roll, dmg_roll, dmg_text, hp_percent: float = None, boss_name: str = None):
                battle = roll + blank + blank + blank + mpreg
                status = "Preparing to cum..."
                print("do_animation: sending initial messages")
                # use send instead of reply to avoid reply-specific behavior
                line1 = await ctx.send(battle)
                line2 = await ctx.send("-------------------------------------")
                line3 = await ctx.send(status)

                await asyncio.sleep(1)
                battle = blank + roll + blank + blank + mpreg
                status = dmg_roll
                await line1.edit(content=battle)
                await line3.edit(content=status)

                await asyncio.sleep(1)
                battle = blank + blank + roll + blank + mpreg
                await line1.edit(content=battle)

                await asyncio.sleep(1)
                battle = blank + blank + blank + roll + mpreg
                await line1.edit(content=battle)

                await asyncio.sleep(1)
                battle = blank + blank + blank + cum + mpreg
                status = dmg_text
                print(dmg_text)
                await line1.edit(content=battle)
                await line3.edit(content=status)

                await asyncio.sleep(1)
                battle = blank + blank + blank + blank + mpreg
                await line1.edit(content=battle)

                # after animation finishes, optionally update status (line3) with a vague HP summary
                try:
                    if hp_percent is not None:
                        pct = float(hp_percent)
                        summary = None
                        name = boss_name or "Boss"
                        if pct >= 80.0:
                            summary = f"{name} seems unscathed."
                        elif pct >= 60.0:
                            summary = f"{name} shows some wounds."
                        elif pct >= 30.0:
                            summary = f"{name} is looking hurt."
                        elif pct >= 5.0:
                            summary = f"{name} is badly wounded."
                        elif pct >= 1.0:
                            summary = f"{name} is barely pregnant!"
                        else:
                            summary = f"{name} has been defeated!"
                        await line3.edit(content=summary)
                except Exception:
                    pass

        # Borpa selection view (in-channel, restrict to invoker)
        class BorpaSelect(discord.ui.View):
            def __init__(self, owner_id: int, timeout=60):
                super().__init__(timeout=timeout)
                self.owner_id = owner_id
                # will be set to the message that contains this view after sending
                self._message = None

                options = [
                    discord.SelectOption(label="Borpa (poor)", value="borpa", description="Send a free borpa in"),
                    discord.SelectOption(label="Borpaspin", value="borpaspin", description="Borpa now spins"),
                    discord.SelectOption(label="Gold Borpaspin", value="gold", description="Spinning golden borpa wow"),
                    discord.SelectOption(label="Rainbow Borpaspin", value="rainbow", description="Rainbow borpa excitement"),
                ]

                self.select = discord.ui.Select(placeholder="Choose which borpa to use", min_values=1, max_values=1, options=options)
                self.select.callback = self.selection_callback
                self.add_item(self.select)

            async def selection_callback(inner_self, interaction: discord.Interaction):
                # only allow the original invoker to interact
                if interaction.user.id != inner_self.owner_id:
                    await interaction.response.send_message("You cannot use this menu.", ephemeral=True)
                    return
                await interaction.response.defer()
                chosen_val = inner_self.select.values[0]

                print(f"selection_callback: user={interaction.user.id} chose={inner_self.select.values}")
                # helper: schedule deletion of the message that holds this view in ~7s
                async def _del_later():
                    try:
                        await asyncio.sleep(7)
                        if inner_self._message:
                            await inner_self._message.delete()
                    except Exception:
                        pass

                # load user row and handle selection
                async with aiosqlite.connect('rolls.db') as db:
                    cursor = await db.execute('SELECT rolls, totalrolls, cums, borpas, goldborpaspins, rainbowborpaspins FROM rolltable WHERE user=?', [playerid])
                    rows = await cursor.fetchall()
                    if not rows:
                        await interaction.followup.send("User not found in database!", ephemeral=True)
                        # schedule deletion even on error
                        if inner_self._message:
                            inner_self._message._del_task = asyncio.create_task(_del_later())
                        return
                    user_row = rows[0]

                    if chosen_val == 'borpa':
                        roll_val = borpa
                        dmg = random.randint(1, 10)
                        dmg_roll = "rolling 1d10"
                        dmg_text = f"{dmg} damage dealt!"
                        await interaction.followup.send("sending the poorpa", ephemeral=True)
                        # apply damage to the boss and report remaining HP
                        try:
                            hp_res, was_killed = await apply_damage(dmg, user_id=playerid, roll_type='borpa')
                            print(f"apply_damage: applied {dmg}, remaining {hp_res.get('hp')}")
                        except Exception:
                            print("apply_damage: failed")
                        try:
                            await ctx.message.add_reaction('✅')
                        except Exception:
                            pass
                        # run animation, then schedule deletion of the menu message
                        print("selection_callback: starting do_animation for borpa")
                        try:
                            pct = 0.0
                            if hp_res and hp_res.get('max_hp'):
                                pct = (int(hp_res.get('hp', 0)) / int(hp_res.get('max_hp', 1))) * 100.0
                        except Exception:
                            pct = None
                        await do_animation(roll_val, dmg_roll, dmg_text, hp_percent=pct, boss_name=hp_res.get('name') if hp_res else None)
                        print("selection_callback: finished do_animation for borpa")
                        if inner_self._message:
                            # Send kill message after animation if needed
                            if was_killed:
                                await ctx.send(f"**MPREG has been defeated by {ctx.author.mention}!**\nIt has now respawned with full health ({hp_res.get('max_hp', 100000):,} HP).")
                            inner_self._message._del_task = asyncio.create_task(_del_later())
                        return

                    # map selection to DB column index and token consumption
                    col_map = {'borpaspin': 3, 'gold': 4, 'rainbow': 5}
                    col_idx = col_map.get(chosen_val)
                    if col_idx is None:
                        await interaction.followup.send("Invalid selection.", ephemeral=True)
                        if inner_self._message:
                            inner_self._message._del_task = asyncio.create_task(_del_later())
                        return

                    current = user_row[col_idx]
                    if not current or int(current) <= 0:
                        await interaction.followup.send("You don't have that borpa to use.", ephemeral=True)
                        try:
                            await ctx.message.add_reaction("🅿️")
                            await ctx.message.add_reaction("🅾️")
                            await ctx.message.add_reaction("🇴")
                            await ctx.message.add_reaction("🇷")
                        except Exception:
                            pass
                        if inner_self._message:
                            inner_self._message._del_task = asyncio.create_task(_del_later())
                        return

                    # consume one
                    if chosen_val == 'borpaspin':
                        await db.execute('UPDATE rolltable SET borpas = borpas - 1 WHERE user=?', [playerid])
                    elif chosen_val == 'gold':
                        await db.execute('UPDATE rolltable SET goldborpaspins = goldborpaspins - 1 WHERE user=?', [playerid])
                    elif chosen_val == 'rainbow':
                        await db.execute('UPDATE rolltable SET rainbowborpaspins = rainbowborpaspins - 1 WHERE user=?', [playerid])
                    await db.commit()

                    # determine roll/dmg
                    if chosen_val == 'borpaspin':
                        roll_val = borpaspin
                        dmg = random.randint(1, 100)
                        dmg_roll = "rolling 1d100"
                    elif chosen_val == 'gold':
                        roll_val = goldborpaspin
                        dmg = random.randint(1, 1000)
                        dmg_roll = "rolling 1d1000"
                    else:
                        roll_val = rainbowborpaspin
                        dmg = random.randint(1, 10000)
                        dmg_roll = "rolling 1d10000"
                    dmg_text = f"{dmg} damage dealt!"

                    # apply damage to the boss and report remaining HP
                    try:
                        hp_res, was_killed = await apply_damage(dmg, user_id=playerid, roll_type=chosen_val)
                        await interaction.followup.send(f"sending {chosen_val} to its death", ephemeral=True)
                        print(f"apply_damage: applied {dmg}, remaining {hp_res.get('hp')}")
                    except Exception:
                        print("apply_damage: failed")
                    try:
                        await ctx.message.add_reaction('✅')
                    except Exception:
                        pass
                    # run animation, then schedule deletion of the menu message ~7s after selection
                    print("selection_callback: starting do_animation for token borpa")
                    try:
                        pct = 0.0
                        if hp_res and hp_res.get('max_hp'):
                            pct = (int(hp_res.get('hp', 0)) / int(hp_res.get('max_hp', 1))) * 100.0
                    except Exception:
                        pct = None
                    await do_animation(roll_val, dmg_roll, dmg_text, hp_percent=pct, boss_name=hp_res.get('name') if hp_res else None)
                    print("selection_callback: finished do_animation for token borpa")
                    if inner_self._message:
                        # Send kill message after animation if needed
                        if was_killed:
                            await ctx.send(f"**MPREG has been defeated by {ctx.author.mention}!**\nIt has now respawned with full health ({hp_res.get('max_hp', 100000):,} HP).")
                        inner_self._message._del_task = asyncio.create_task(_del_later())

        # Show menu in-channel and keep a reference to the sent message on the view
        view = BorpaSelect(owner_id=playerid)
        sendie = ctx.author.name + " select which borpa to send:"
        sent_msg = await ctx.send(sendie, view=view)
        # attach the message object to the view so the callback can delete it later
        view._message = sent_msg
        return
        
    
async def setup(bot):
    await bot.add_cog(cuemCog(bot))
    print('cuem cog loaded')

####
# The idea of this is to make a 5x5? slot machine or something similar
#
# spinner will spin to do dmg to a boss 
#