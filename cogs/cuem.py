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
gigampreg = '<:gigampreg:1449350064110833779>'



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
        self.gigampreg_vulnerable_until = None
        self.boss_state_path = 'configs/boss_state.json'
        try:
            with open(self.boss_state_path, 'r') as f:
                data = json.load(f)
                self.active_boss = data.get('active_boss', 'mpreg')
        except (FileNotFoundError, json.JSONDecodeError):
            self.active_boss = 'mpreg'

    @commands.command()
    @commands.is_owner()
    async def toggleboss(self, ctx):
        """Toggles the active boss between mpreg and gigampreg."""
        if self.active_boss == 'mpreg':
            self.active_boss = 'gigampreg'
        else:
            self.active_boss = 'mpreg'
        
        try:
            with open(self.boss_state_path, 'w') as f:
                json.dump({'active_boss': self.active_boss}, f)
        except Exception as e:
            print(f"Error saving boss state: {e}")

        await ctx.send(f"Active boss set to: **{self.active_boss}**")

    @commands.command()
    @commands.cooldown(2, 60, commands.BucketType.user)
    #@commands.is_owner()
    async def cum2(self, ctx):
        """Usage: .cum2 -> opens the in-channel borpa selection menu for the active boss"""
        if ctx.channel.id not in channel_id:
            return

        playerid = ctx.author.id

        if self.active_boss == 'gigampreg':
            current_boss_path = 'configs/gigampreg_hp.json'
            current_boss_name = 'gigampreg'
            current_boss_max = 500000
            current_boss_emoji = gigampreg
            current_prep_text = "Preparing to cum on GIGA..."
        else:
            current_boss_path = 'configs/mpreg_hp.json'
            current_boss_name = 'mpreg'
            current_boss_max = 100000
            current_boss_emoji = mpreg
            current_prep_text = "Preparing to cum..."

        # Helper to apply damage to the active boss
        async def apply_damage(amount: int, user_id: int = None, roll_type: str = None):
            def _sync_apply():
                path = current_boss_path
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception:
                    data = {"name": current_boss_name, "hp": current_boss_max, "max_hp": current_boss_max}
                try:
                    data['old_hp'] = int(data.get('hp', 0))
                    hp = int(data.get('hp', 0))
                except Exception:
                    hp = 0

                boss_killed = (hp - int(amount)) <= 0
                hp = max(0, hp - int(amount))

                if boss_killed and hp == 0:
                    data['hp'] = data.get('max_hp', current_boss_max) # Reset to max HP
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
                async with aiosqlite.connect('db/rolls.db') as db:
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
                battle = roll + blank + blank + blank + current_boss_emoji
                status = current_prep_text
                
                if self.active_boss == 'gigampreg':
                    if self.gigampreg_vulnerable_until and datetime.datetime.utcnow() < self.gigampreg_vulnerable_until:
                        status = "GIGAMPREG is vulnerable!"
                    else:
                        status = "GIGAMPREG is guarded..."

                print("do_animation: sending initial messages")
                # use send instead of reply to avoid reply-specific behavior
                line1 = await ctx.send(battle)
                line2 = await ctx.send("-------------------------------------")
                line3 = await ctx.send(status)

                await asyncio.sleep(1)
                battle = blank + roll + blank + blank + current_boss_emoji
                status = dmg_roll
                await line1.edit(content=battle)
                await line3.edit(content=status)

                await asyncio.sleep(1)
                battle = blank + blank + roll + blank + current_boss_emoji
                await line1.edit(content=battle)

                await asyncio.sleep(1)
                battle = blank + blank + blank + roll + current_boss_emoji
                await line1.edit(content=battle)

                await asyncio.sleep(1)
                battle = blank + blank + blank + cum + current_boss_emoji
                status = dmg_text
                print(dmg_text)
                await line1.edit(content=battle)
                await line3.edit(content=status)

                await asyncio.sleep(1)
                battle = blank + blank + blank + blank + current_boss_emoji
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

                self.select = discord.ui.Select(placeholder=f"Choose which borpa to use against {current_boss_name.upper()}", min_values=1, max_values=1, options=options)
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
                async with aiosqlite.connect('db/rolls.db') as db:
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
                        
                        if self.active_boss == 'gigampreg':
                            is_vulnerable = self.gigampreg_vulnerable_until and datetime.datetime.utcnow() < self.gigampreg_vulnerable_until
                            if not is_vulnerable:
                                if random.random() < 0.50:
                                    dmg = 0
                                    dmg_text = "Bounced off! 0 damage."
                            
                            if dmg > 0 and is_vulnerable:
                                dmg *= 2
                                dmg_text = f"{dmg} damage dealt! (x2)"

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
                                await ctx.send(f"**{current_boss_name.upper()} has been defeated by {ctx.author.mention}!**\nIt has now respawned with full health ({hp_res.get('max_hp', current_boss_max):,} HP).")
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

                    if self.active_boss == 'gigampreg':
                        is_vulnerable = self.gigampreg_vulnerable_until and datetime.datetime.utcnow() < self.gigampreg_vulnerable_until
                        shield_break = False
                        
                        if chosen_val == 'rainbow':
                            if not is_vulnerable and random.random() < 0.33:
                                shield_break = True
                        elif not is_vulnerable:
                            if random.random() < 0.50:
                                dmg = 0
                                dmg_text = "Bounced off! 0 damage."
                        
                        if dmg > 0 and is_vulnerable:
                            dmg *= 2
                            dmg_text = f"{dmg} damage dealt! (x2)"
                        
                        if shield_break:
                            self.gigampreg_vulnerable_until = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
                            dmg_text = f"SHIELD BROKEN! {dmg} damage!"
                            await ctx.send(f"**{current_boss_name.upper()}'s shield has been BROKEN! Vulnerable for 60 seconds!**")
                            
                            async def recover():
                                await asyncio.sleep(60)
                                if self.gigampreg_vulnerable_until and datetime.datetime.utcnow() >= self.gigampreg_vulnerable_until:
                                    await ctx.send(f"**{current_boss_name.upper()} has regained his stance!**")
                            asyncio.create_task(recover())

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
                            await ctx.send(f"**{current_boss_name.upper()} has been defeated by {ctx.author.mention}!**\nIt has now respawned with full health ({hp_res.get('max_hp', current_boss_max):,} HP).")
                        inner_self._message._del_task = asyncio.create_task(_del_later())

        # Show menu in-channel and keep a reference to the sent message on the view
        view = BorpaSelect(owner_id=playerid)
        sendie = ctx.author.name + f" select which borpa to send against {current_boss_name.upper()}:"
        sent_msg = await ctx.send(sendie, view=view)
        # attach the message object to the view so the callback can delete it later
        view._message = sent_msg
        return
    
async def setup(bot):
    await bot.add_cog(cuemCog(bot))
    print('cuem cog loaded')
