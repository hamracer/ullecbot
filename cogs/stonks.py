import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
import io
import re
import aiohttp
from datetime import datetime, timezone, timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestQuoteRequest, StockLatestTradeRequest, StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import GetAssetsRequest
    from alpaca.trading.enums import AssetClass, AssetStatus
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False

PORTFOLIO_FILE = "db/portfolios.json"
ALPACA_CONFIG_FILE = "configs/alpaca.json"
STARTING_CASH = 100000.0

class stonksCog(commands.Cog, name="stonks"):
    def __init__(self, bot):
        self.bot = bot
        self.alpaca_client = None
        self.trading_client = None
        self.cached_assets = []
        self.load_alpaca_client()
        
        # Ensure portfolio file exists
        if not os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, "w") as f:
                json.dump({}, f)

    def load_alpaca_client(self):
        if os.path.exists(ALPACA_CONFIG_FILE) and ALPACA_AVAILABLE:
            try:
                with open(ALPACA_CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    api_key = config.get("API_KEY")
                    secret_key = config.get("SECRET_KEY")
                    if api_key and secret_key and api_key != "YOUR_API_KEY":
                        self.alpaca_client = StockHistoricalDataClient(api_key, secret_key)
                        self.trading_client = TradingClient(api_key, secret_key, paper=True)
                        print("Alpaca Market Data & Trading Clients initialized.")
                        return True
                    else:
                        print("Alpaca API keys not set. Please update configs/alpaca.json")
            except Exception as e:
                print(f"Error loading Alpaca config: {e}")
        return False

    def get_market_assets(self):
        if not self.cached_assets and self.trading_client:
            try:
                req = GetAssetsRequest(asset_class=AssetClass.US_EQUITY, status=AssetStatus.ACTIVE)
                assets = self.trading_client.get_all_assets(req)
                self.cached_assets = [a.symbol for a in assets if getattr(a, "tradable", False)]
                print(f"Cached {len(self.cached_assets)} tradeable US market assets.")
            except Exception as e:
                print(f"Error fetching market assets: {e}")
        return self.cached_assets

    def load_portfolios(self):
        try:
            with open(PORTFOLIO_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def save_portfolios(self, data):
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def get_price(self, symbol: str) -> float:
        if not self.alpaca_client:
            if not self.load_alpaca_client():
                raise Exception("Alpaca Client not initialized. Check API keys in configs/alpaca.json")
        
        # First try fetching latest trade price
        try:
            trade_req = StockLatestTradeRequest(symbol_or_symbols=symbol)
            trades = self.alpaca_client.get_stock_latest_trade(trade_req)
            if symbol in trades:
                trade = trades[symbol]
                price = getattr(trade, "price", None)
                if price is None and isinstance(trade, dict):
                    price = trade.get("price")
                if price and float(price) > 0:
                    return float(price)
        except Exception:
            pass

        # Fallback to latest quote
        quote_req = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quotes = self.alpaca_client.get_stock_latest_quote(quote_req)
        if symbol in quotes:
            quote = quotes[symbol]
            price = getattr(quote, "ask_price", None)
            if price is None and isinstance(quote, dict):
                price = quote.get("ask_price", 0)
            if not price or float(price) == 0:
                price = getattr(quote, "bid_price", None)
                if price is None and isinstance(quote, dict):
                    price = quote.get("bid_price", 0)
            if price and float(price) > 0:
                return float(price)
        raise Exception(f"No price data found for {symbol}")

    def get_holding_info(self, holding_data):
        if isinstance(holding_data, (int, float)):
            return int(holding_data), 0.0, 0.0
        elif isinstance(holding_data, dict):
            shares = int(holding_data.get("shares", 0))
            avg_cost = float(holding_data.get("avg_cost", 0.0))
            total_invested = float(holding_data.get("total_invested", avg_cost * shares))
            return shares, avg_cost, total_invested
        return 0, 0.0, 0.0

    @app_commands.command(name="stonks_join", description="Join the stock market competition and get your starting cash!")
    async def stonks_join(self, interaction: discord.Interaction):
        portfolios = self.load_portfolios()
        user_id = str(interaction.user.id)
        
        if user_id in portfolios:
            await interaction.response.send_message("You have already joined the competition!", ephemeral=True)
            return
            
        portfolios[user_id] = {
            "cash": STARTING_CASH,
            "holdings": {},
            "history": []
        }
        self.save_portfolios(portfolios)
        await interaction.response.send_message(f"Welcome to the competition, {interaction.user.mention}! You have been granted ${STARTING_CASH:,.2f} to start trading.")

    async def get_company_info(self, symbol: str) -> tuple[str, str]:
        name = symbol
        if self.trading_client:
            try:
                asset = self.trading_client.get_asset(symbol)
                if asset and hasattr(asset, "name") and asset.name:
                    name = asset.name
            except Exception:
                pass

        description = ""
        try:
            clean_name = re.sub(r' (Common Stock|Class [A-Z]|Ordinary Shares|Depositary Shares|Inc\.|Corp\.|Ltd\.|LLC|PLC).*', '', name, flags=re.I).strip()
            headers = {'User-Agent': 'UllecBot/1.0 (https://github.com/ullecbot; contact@example.com)'}
            async with aiohttp.ClientSession(headers=headers) as session:
                url = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={clean_name}%20company&format=json&utf8=1'
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=4)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get('query', {}).get('search', [])
                        if results:
                            title = results[0]['title']
                            summary_url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{title}'
                            async with session.get(summary_url, timeout=aiohttp.ClientTimeout(total=4)) as sum_resp:
                                if sum_resp.status == 200:
                                    s_data = await sum_resp.json()
                                    extract = s_data.get('extract', '')
                                    if extract:
                                        sentences = re.split(r'(?<=[.!?])\s+', extract)
                                        description = ' '.join(sentences[:2])
        except Exception:
            description = ""
            
        return name, description

    @app_commands.command(name="buy", description="Buy shares of a stock.")
    async def buy(self, interaction: discord.Interaction, symbol: str, quantity: int):
        if quantity <= 0:
            await interaction.response.send_message("Quantity must be greater than 0.", ephemeral=True)
            return

        symbol = symbol.upper()
        user_id = str(interaction.user.id)
        portfolios = self.load_portfolios()

        if user_id not in portfolios:
            await interaction.response.send_message("You haven't joined the competition yet! Use `/stonks_join` to start.", ephemeral=True)
            return

        try:
            price = self.get_price(symbol)
        except Exception as e:
            await interaction.response.send_message(f"Error fetching price for {symbol}: {e}", ephemeral=True)
            return
            
        if price <= 0:
            await interaction.response.send_message(f"Could not get a valid price for {symbol}.", ephemeral=True)
            return

        total_cost = price * quantity
        user_cash = portfolios[user_id]["cash"]

        if total_cost > user_cash:
            await interaction.response.send_message(f"Insufficient funds! You need **${total_cost:,.2f}** but only have **${user_cash:,.2f}**.", ephemeral=True)
            return

        # Execute trade with cost basis tracking
        user_data = portfolios[user_id]
        holdings = user_data.setdefault("holdings", {})
        old_shares, old_avg_cost, old_total_invested = self.get_holding_info(holdings.get(symbol, 0))
        
        new_shares = old_shares + quantity
        new_total_invested = old_total_invested + total_cost
        new_avg_cost = new_total_invested / new_shares if new_shares > 0 else price
        
        holdings[symbol] = {
            "shares": new_shares,
            "avg_cost": new_avg_cost,
            "total_invested": new_total_invested
        }
        user_data["cash"] -= total_cost
        
        # Log to trade history
        history = user_data.setdefault("history", [])
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "BUY",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "total": total_cost
        })
        if len(history) > 50:
            user_data["history"] = history[-50:]
        
        self.save_portfolios(portfolios)
        
        new_cash = user_data["cash"]

        embed = discord.Embed(
            title=f"✅ Purchased {quantity:,} share(s) of {symbol}",
            color=discord.Color.green()
        )
        embed.add_field(name="💵 Execution Price", value=f"${price:,.2f}", inline=True)
        embed.add_field(name="🧾 Total Cost", value=f"${total_cost:,.2f}", inline=True)
        embed.add_field(name="💰 Remaining Cash", value=f"**${new_cash:,.2f}**", inline=False)
        embed.add_field(name=f"📦 Position Summary", value=f"**{new_shares:,}** shares @ **${new_avg_cost:,.2f}** avg", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy_random", description="Buy a random mystery stock!")
    @app_commands.describe(
        spend_amount="Total dollar amount to spend (e.g. 5000)",
        quantity="Number of shares to buy (defaults to 1 if spend_amount is not set)"
    )
    async def buy_random(self, interaction: discord.Interaction, spend_amount: float = None, quantity: int = None):
        user_id = str(interaction.user.id)
        portfolios = self.load_portfolios()

        if user_id not in portfolios:
            await interaction.response.send_message("You haven't joined the competition yet! Use `/stonks_join` to start.", ephemeral=True)
            return

        user_cash = portfolios[user_id]["cash"]
        if user_cash <= 0:
            await interaction.response.send_message("You have no cash left to invest!", ephemeral=True)
            return

        await interaction.response.defer()

        # Get all tradeable assets on the market
        market_assets = self.get_market_assets()
        if not market_assets:
            await interaction.followup.send("Market assets are currently unavailable. Please try again shortly!", ephemeral=True)
            return

        # Pick random candidate stocks across the entire market
        sampled_stocks = random.sample(market_assets, min(25, len(market_assets)))
        chosen_symbol = None
        price = 0.0

        for candidate in sampled_stocks:
            try:
                candidate_price = self.get_price(candidate)
                if candidate_price and candidate_price > 0:
                    chosen_symbol = candidate
                    price = candidate_price
                    break
            except Exception:
                continue

        if not chosen_symbol or price <= 0:
            await interaction.followup.send("Could not fetch a valid stock price at the moment. Try again shortly!", ephemeral=True)
            return

        # Determine shares to buy
        if spend_amount is not None:
            if spend_amount <= 0:
                await interaction.followup.send("Spend amount must be greater than $0.", ephemeral=True)
                return
            if spend_amount > user_cash:
                await interaction.followup.send(f"You don't have enough cash! You specified **${spend_amount:,.2f}** but only have **${user_cash:,.2f}**.", ephemeral=True)
                return
            
            calculated_qty = int(spend_amount // price)
            if calculated_qty < 1:
                await interaction.followup.send(f"🎲 Rolled **{chosen_symbol}** at **${price:,.2f}**/share, but your spend amount of **${spend_amount:,.2f}** is not enough for 1 full share.", ephemeral=True)
                return
            actual_quantity = calculated_qty
        else:
            actual_quantity = quantity if (quantity is not None and quantity > 0) else 1

        total_cost = price * actual_quantity
        if total_cost > user_cash:
            await interaction.followup.send(f"🎲 Rolled **{chosen_symbol}** at **${price:,.2f}**/share! {actual_quantity:,} share(s) cost **${total_cost:,.2f}**, but you only have **${user_cash:,.2f}**.", ephemeral=True)
            return

        # Execute trade with cost basis tracking
        user_data = portfolios[user_id]
        holdings = user_data.setdefault("holdings", {})
        old_shares, old_avg_cost, old_total_invested = self.get_holding_info(holdings.get(chosen_symbol, 0))
        
        new_shares = old_shares + actual_quantity
        new_total_invested = old_total_invested + total_cost
        new_avg_cost = new_total_invested / new_shares if new_shares > 0 else price
        
        holdings[chosen_symbol] = {
            "shares": new_shares,
            "avg_cost": new_avg_cost,
            "total_invested": new_total_invested
        }
        user_data["cash"] -= total_cost
        
        # Log to trade history
        history = user_data.setdefault("history", [])
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "BUY",
            "symbol": chosen_symbol,
            "quantity": actual_quantity,
            "price": price,
            "total": total_cost
        })
        if len(history) > 50:
            user_data["history"] = history[-50:]
        
        self.save_portfolios(portfolios)
        
        new_cash = user_data["cash"]

        embed = discord.Embed(
            title=f"🎰 Mystery Stock Unlocked: {chosen_symbol}!",
            description=f"The wheel of stonks has spoken and bought **{actual_quantity:,} share(s)** of **{chosen_symbol}**!",
            color=discord.Color.purple()
        )
        embed.add_field(name="🎲 Selected Stock", value=f"**{chosen_symbol}**", inline=True)
        embed.add_field(name="💵 Execution Price", value=f"${price:,.2f}", inline=True)
        embed.add_field(name="🧾 Total Cost", value=f"${total_cost:,.2f}", inline=True)
        embed.add_field(name="💰 Remaining Cash", value=f"**${new_cash:,.2f}**", inline=False)
        embed.add_field(name="📦 Position Summary", value=f"**{new_shares:,}** shares @ **${new_avg_cost:,.2f}** avg", inline=False)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="sell", description="Sell shares of a stock.")
    async def sell(self, interaction: discord.Interaction, symbol: str, quantity: int):
        if quantity <= 0:
            await interaction.response.send_message("Quantity must be greater than 0.", ephemeral=True)
            return

        symbol = symbol.upper()
        user_id = str(interaction.user.id)
        portfolios = self.load_portfolios()

        if user_id not in portfolios:
            await interaction.response.send_message("You haven't joined the competition yet! Use `/stonks_join` to start.", ephemeral=True)
            return

        user_data = portfolios[user_id]
        holdings = user_data.setdefault("holdings", {})
        old_shares, old_avg_cost, old_total_invested = self.get_holding_info(holdings.get(symbol, 0))

        if old_shares < quantity:
            await interaction.response.send_message(f"You don't own enough shares of **{symbol}** to sell {quantity:,} (you currently own {old_shares:,}).", ephemeral=True)
            return

        try:
            price = self.get_price(symbol)
        except Exception as e:
            await interaction.response.send_message(f"Error fetching price for {symbol}: {e}", ephemeral=True)
            return
            
        if price <= 0:
            await interaction.response.send_message(f"Could not get a valid price for {symbol}.", ephemeral=True)
            return

        total_revenue = price * quantity

        # Execute trade
        new_shares = old_shares - quantity
        if new_shares <= 0:
            if symbol in holdings:
                del holdings[symbol]
        else:
            new_total_invested = new_shares * old_avg_cost
            holdings[symbol] = {
                "shares": new_shares,
                "avg_cost": old_avg_cost,
                "total_invested": new_total_invested
            }

        user_data["cash"] += total_revenue
        
        # Log to trade history
        history = user_data.setdefault("history", [])
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "SELL",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "total": total_revenue
        })
        if len(history) > 50:
            user_data["history"] = history[-50:]
            
        self.save_portfolios(portfolios)
        
        new_cash = user_data["cash"]
        remaining_owned = new_shares

        embed = discord.Embed(
            title=f"💸 Sold {quantity:,} share(s) of {symbol}",
            color=discord.Color.blue()
        )
        embed.add_field(name="💵 Sale Price", value=f"${price:,.2f}", inline=True)
        embed.add_field(name="📈 Total Proceeds", value=f"+${total_revenue:,.2f}", inline=True)
        embed.add_field(name="💰 Current Cash", value=f"**${new_cash:,.2f}**", inline=False)
        embed.add_field(name=f"📦 Remaining {symbol} Owned", value=f"{remaining_owned:,} shares", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="portfolio", description="View your or another user's stock portfolio, cost basis, and net worth.")
    @app_commands.describe(user="The user whose portfolio you want to view (defaults to yourself)")
    async def portfolio(self, interaction: discord.Interaction, user: discord.Member = None):
        await interaction.response.defer()
        
        target_user = user or interaction.user
        user_id = str(target_user.id)
        portfolios = self.load_portfolios()

        if user_id not in portfolios:
            if user and user != interaction.user:
                await interaction.followup.send(f"**{target_user.display_name}** hasn't joined the competition yet!", ephemeral=True)
            else:
                await interaction.followup.send("You haven't joined the competition yet! Use `/stonks_join` to start.", ephemeral=True)
            return

        user_data = portfolios[user_id]
        cash = user_data.get("cash", 0.0)
        holdings = user_data.get("holdings", {})
        
        total_holdings_value = 0.0
        holdings_lines = []
        
        for symbol, h_data in holdings.items():
            shares, avg_cost, _ = self.get_holding_info(h_data)
            if shares <= 0:
                continue
                
            try:
                price = self.get_price(symbol)
                value = price * shares
                total_holdings_value += value
                
                if avg_cost > 0:
                    cost_basis = avg_cost * shares
                    pnl = value - cost_basis
                    pnl_pct = (pnl / cost_basis) * 100
                    emoji = "🟢" if pnl >= 0 else "🔴"
                    sign = "+" if pnl >= 0 else ""
                    holdings_lines.append(
                        f"{emoji} **{symbol}**: {shares:,} shares @ ${avg_cost:,.2f} avg (Now: ${price:,.2f})\n"
                        f"   └ Value: **${value:,.2f}** | P/L: **{sign}${pnl:,.2f} ({sign}{pnl_pct:.2f}%)**"
                    )
                else:
                    holdings_lines.append(
                        f"🔹 **{symbol}**: {shares:,} shares @ ${price:,.2f} (Value: **${value:,.2f}**)"
                    )
            except:
                holdings_lines.append(f"⚠️ **{symbol}**: {shares:,} shares (Price unavailable)")
                
        positions_text = "\n".join(holdings_lines) if holdings_lines else "No active holdings."
        net_worth = cash + total_holdings_value
        total_return = net_worth - STARTING_CASH
        total_return_pct = (total_return / STARTING_CASH) * 100
        return_sign = "+" if total_return >= 0 else ""
        return_emoji = "📈" if total_return >= 0 else "📉"
        
        embed_color = discord.Color.green() if total_return >= 0 else discord.Color.red()
        embed = discord.Embed(title=f"📊 {target_user.display_name}'s Portfolio", color=embed_color)
        
        embed.add_field(name="💰 Cash Balance", value=f"${cash:,.2f}", inline=True)
        embed.add_field(name="📦 Holdings Value", value=f"${total_holdings_value:,.2f}", inline=True)
        embed.add_field(name="💎 Total Net Worth", value=f"**${net_worth:,.2f}**", inline=False)
        embed.add_field(name=f"{return_emoji} Total Overall Return", value=f"**{return_sign}${total_return:,.2f} ({return_sign}{total_return_pct:.2f}%)**", inline=False)
        embed.add_field(name="📋 Positions & Cost Basis", value=positions_text, inline=False)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="trade_history", description="View recent transactions and purchase history.")
    @app_commands.describe(user="The user whose trade history you want to view (defaults to yourself)")
    async def trade_history(self, interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        user_id = str(target_user.id)
        portfolios = self.load_portfolios()

        if user_id not in portfolios:
            if user and user != interaction.user:
                await interaction.response.send_message(f"**{target_user.display_name}** hasn't joined the competition yet!", ephemeral=True)
            else:
                await interaction.response.send_message("You haven't joined the competition yet! Use `/stonks_join` to start.", ephemeral=True)
            return

        history = portfolios[user_id].get("history", [])
        if not history:
            name_ref = f"**{target_user.display_name}** has" if user and user != interaction.user else "You have"
            await interaction.response.send_message(f"{name_ref} no recorded trade history yet!", ephemeral=True)
            return

        embed = discord.Embed(title=f"📜 {target_user.display_name}'s Trade History", color=discord.Color.blue())
        
        for item in reversed(history[-10:]):
            ttype = item.get("type", "TRADE")
            emoji = "🟢 BUY" if ttype == "BUY" else "🔴 SELL"
            sym = item.get("symbol", "N/A")
            qty = item.get("quantity", 0)
            prc = item.get("price", 0.0)
            tot = item.get("total", 0.0)
            ts = item.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(ts)
                time_str = dt.strftime("%b %d, %H:%M UTC")
            except:
                time_str = ts
            
            embed.add_field(
                name=f"{emoji} {qty:,}x {sym} @ ${prc:,.2f}",
                value=f"Total: **${tot:,.2f}** • *{time_str}*",
                inline=False
            )
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the top investors in the competition.")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        portfolios = self.load_portfolios()
        if not portfolios:
            await interaction.followup.send("Nobody has joined the competition yet!")
            return
            
        leaderboard_data = []
        
        for uid, data in portfolios.items():
            cash = data.get("cash", 0.0)
            total_value = cash
            for symbol, h_data in data.get("holdings", {}).items():
                shares, _, _ = self.get_holding_info(h_data)
                if shares > 0:
                    try:
                        price = self.get_price(symbol)
                        total_value += (price * shares)
                    except:
                        pass
            leaderboard_data.append((uid, total_value))
            
        # Sort by total value descending
        leaderboard_data.sort(key=lambda x: x[1], reverse=True)
        
        embed = discord.Embed(title="🏆 Stonks Leaderboard", color=discord.Color.gold())
        
        for i, (uid, net_worth) in enumerate(leaderboard_data[:10]):
            member = interaction.guild.get_member(int(uid))
            name = member.display_name if member else f"User {uid}"
            
            # Add medal emojis for top 3
            prefix = "🏅"
            if i == 0: prefix = "🥇"
            elif i == 1: prefix = "🥈"
            elif i == 2: prefix = "🥉"
            
            total_return = net_worth - STARTING_CASH
            return_sign = "+" if total_return >= 0 else ""
            
            embed.add_field(
                name=f"{prefix} #{i+1} {name}",
                value=f"Net Worth: **${net_worth:,.2f}** ({return_sign}${total_return:,.2f})",
                inline=False
            )
            
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="stock", description="Check a stock's live price, company summary, and historical chart.")
    @app_commands.describe(symbol="Stock ticker symbol (e.g. AAPL, NVDA, NDSN)", period="Time period for the chart (default 1M)")
    @app_commands.choices(period=[
        app_commands.Choice(name="1 Week (1W)", value="1W"),
        app_commands.Choice(name="1 Month (1M)", value="1M"),
        app_commands.Choice(name="3 Months (3M)", value="3M"),
        app_commands.Choice(name="6 Months (6M)", value="6M"),
        app_commands.Choice(name="1 Year (1Y)", value="1Y"),
    ])
    async def stock(self, interaction: discord.Interaction, symbol: str, period: app_commands.Choice[str] = None):
        await interaction.response.defer()
        symbol = symbol.upper()
        selected_period = period.value if period else "1M"

        period_map = {
            "1W": (timedelta(days=7), TimeFrame.Hour),
            "1M": (timedelta(days=30), TimeFrame.Day),
            "3M": (timedelta(days=90), TimeFrame.Day),
            "6M": (timedelta(days=180), TimeFrame.Day),
            "1Y": (timedelta(days=365), TimeFrame.Day),
        }
        
        delta, tf = period_map.get(selected_period, (timedelta(days=30), TimeFrame.Day))
        start_time = datetime.now(timezone.utc) - delta

        if not self.alpaca_client:
            if not self.load_alpaca_client():
                await interaction.followup.send("Alpaca Client not initialized. Check API keys in configs/alpaca.json", ephemeral=True)
                return

        # Fetch current price
        try:
            curr_price = self.get_price(symbol)
        except Exception as e:
            await interaction.followup.send(f"Error fetching price for **{symbol}**: {e}", ephemeral=True)
            return

        # Fetch company name and 2-line description
        company_name, description = await self.get_company_info(symbol)

        try:
            req = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=start_time
            )
            bar_set = self.alpaca_client.get_stock_bars(req)
            
            bars = []
            if hasattr(bar_set, "data") and symbol in bar_set.data:
                bars = bar_set.data[symbol]
            elif hasattr(bar_set, symbol):
                bars = getattr(bar_set, symbol)
            elif isinstance(bar_set, dict) and symbol in bar_set:
                bars = bar_set[symbol]
            else:
                try:
                    bars = bar_set[symbol]
                except Exception:
                    bars = []

            if not bars or len(bars) < 2:
                # If historical data is missing, send rich embed without chart
                embed = discord.Embed(
                    title=f"{company_name} ({symbol})",
                    description=description if description else "*No company summary available.*",
                    color=discord.Color.blue()
                )
                embed.add_field(name="💵 Current Price", value=f"**${curr_price:,.2f}**", inline=True)
                await interaction.followup.send(embed=embed)
                return
            
            dates = [b.timestamp for b in bars]
            prices = [float(b.close) for b in bars]
            
            open_price = prices[0]
            diff = curr_price - open_price
            pct_change = (diff / open_price) * 100 if open_price > 0 else 0.0
            high_price = max(prices)
            low_price = min(prices)
            
            is_up = diff >= 0
            color_hex = "#2ecc71" if is_up else "#e74c3c"
            
            # Generate chart with matplotlib
            fig, ax = plt.subplots(figsize=(9, 4.5), dpi=150)
            fig.patch.set_facecolor("#1e1e24")
            ax.set_facecolor("#1e1e24")
            
            ax.plot(dates, prices, color=color_hex, linewidth=2)
            ax.fill_between(dates, prices, min(prices) * 0.998, color=color_hex, alpha=0.15)
            
            ax.set_title(f"{symbol} Price Chart ({selected_period})", color="white", fontsize=13, fontweight="bold", pad=12)
            ax.tick_params(colors="white", which="both")
            ax.grid(True, linestyle="--", alpha=0.2, color="white")
            
            if selected_period == "1W":
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
            fig.autofmt_xdate()
            
            for spine in ax.spines.values():
                spine.set_color("#444444")
                
            ax.set_ylabel("Price ($)", color="white", fontsize=10)
            
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
            plt.close(fig)
            buf.seek(0)
            
            embed_color = discord.Color.green() if is_up else discord.Color.red()
            sign = "+" if diff >= 0 else ""
            
            embed = discord.Embed(
                title=f"{company_name} ({symbol})",
                description=description if description else "*No company summary available.*",
                color=embed_color
            )
            embed.add_field(name="💵 Current Price", value=f"**${curr_price:,.2f}**", inline=True)
            embed.add_field(name=f"📊 Change ({selected_period})", value=f"**{sign}${diff:,.2f} ({sign}{pct_change:.2f}%)**", inline=True)
            embed.add_field(name="📈 Period Range", value=f"${low_price:,.2f} - ${high_price:,.2f}", inline=True)
            
            file = discord.File(buf, filename=f"{symbol}_chart.png")
            embed.set_image(url=f"attachment://{symbol}_chart.png")
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(f"Error generating stock overview for {symbol}: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(stonksCog(bot))
    print('stonks cog loaded')
