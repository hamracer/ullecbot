import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
import io
import re
import uuid
import aiohttp
from datetime import datetime, timezone, timedelta, date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.historical.option import OptionHistoricalDataClient
    from alpaca.data.requests import (
        StockLatestQuoteRequest,
        StockLatestTradeRequest,
        StockBarsRequest,
        OptionChainRequest,
        OptionLatestQuoteRequest
    )
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
STONKS_CHANNEL_ID = 1542935779448197190

class stonksCog(commands.Cog, name="stonks"):
    def __init__(self, bot):
        self.bot = bot
        self.alpaca_client = None
        self.trading_client = None
        self.option_client = None
        self.cached_assets = []
        self.load_alpaca_client()
        
        # Ensure portfolio file exists
        if not os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, "w") as f:
                json.dump({}, f)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.channel_id != STONKS_CHANNEL_ID:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"Stonks commands can only be used in <#{STONKS_CHANNEL_ID}>!",
                    ephemeral=True
                )
            return False
        return True

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            return
        print(f"Error in stonks command: {error}")

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
                        self.option_client = OptionHistoricalDataClient(api_key, secret_key)
                        print("Alpaca Market Data, Trading & Options Clients initialized.")
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

    def evaluate_contract(self, pos: dict, current_price: float):
        pos_type = pos.get("type", "LONG")
        entry_price = float(pos.get("entry_price", 0.0))
        margin = float(pos.get("margin", 0.0))
        shares = float(pos.get("shares", 0.0))
        liq_price = float(pos.get("liquidation_price", 0.0))
        
        is_liquidated = False
        if pos_type == "LONG":
            if current_price <= liq_price:
                is_liquidated = True
            pnl = (current_price - entry_price) * shares
        else:
            if current_price >= liq_price:
                is_liquidated = True
            pnl = (entry_price - current_price) * shares
            
        if is_liquidated:
            pnl = -margin
            equity = 0.0
            roe = -100.0
        else:
            equity = max(0.0, margin + pnl)
            roe = (pnl / margin) * 100.0 if margin > 0 else 0.0
            if equity <= 0.0:
                is_liquidated = True
                equity = 0.0
                roe = -100.0
                
        return is_liquidated, pnl, equity, roe

    def parse_occ_symbol(self, occ: str):
        match = re.match(r"^([A-Z]+)(\d{6})([CP])(\d{8})$", occ.upper())
        if match:
            ticker, exp_str, cp, strike_str = match.groups()
            exp_date = datetime.strptime(exp_str, "%y%m%d").date()
            opt_type = "CALL" if cp == "C" else "PUT"
            strike = int(strike_str) / 1000.0
            return ticker, exp_date, opt_type, strike
        return None, None, None, None

    def build_occ_symbol(self, symbol: str, exp_date: date, opt_type: str, strike: float) -> str:
        exp_str = exp_date.strftime("%y%m%d")
        type_char = "C" if opt_type.upper() == "CALL" else "P"
        strike_int = int(round(strike * 1000))
        return f"{symbol.upper()}{exp_str}{type_char}{strike_int:08d}"

    def get_option_quote(self, contract_symbol: str) -> tuple[float, float, float]:
        if not self.option_client:
            if not self.load_alpaca_client():
                raise Exception("Alpaca Option Client not initialized.")
        try:
            req = OptionLatestQuoteRequest(symbol_or_symbols=contract_symbol)
            res = self.option_client.get_option_latest_quote(req)
            if contract_symbol in res:
                q = res[contract_symbol]
                ask = getattr(q, "ask_price", 0.0) or (q.get("ask_price", 0.0) if isinstance(q, dict) else 0.0)
                bid = getattr(q, "bid_price", 0.0) or (q.get("bid_price", 0.0) if isinstance(q, dict) else 0.0)
                ask = float(ask) if ask else 0.0
                bid = float(bid) if bid else 0.0
                mid = (ask + bid) / 2.0 if (ask > 0 and bid > 0) else (ask or bid or 0.0)
                return bid, ask, mid
        except Exception as e:
            print(f"Error fetching quote for {contract_symbol}: {e}")
        return 0.0, 0.0, 0.0

    def get_option_chain_data(self, symbol: str) -> list[dict]:
        if not self.option_client:
            if not self.load_alpaca_client():
                raise Exception("Alpaca Option Client not initialized.")
        req = OptionChainRequest(underlying_symbol=symbol)
        chain = self.option_client.get_option_chain(req)
        contracts = []
        for sym, data in chain.items():
            ticker, exp_date, opt_type, strike = self.parse_occ_symbol(sym)
            if not ticker:
                continue
            quote = getattr(data, "latest_quote", None)
            ask = getattr(quote, "ask_price", 0.0) if quote else 0.0
            bid = getattr(quote, "bid_price", 0.0) if quote else 0.0
            ask = float(ask) if ask else 0.0
            bid = float(bid) if bid else 0.0
            mid = (ask + bid) / 2.0 if (ask > 0 and bid > 0) else (ask or bid or 0.0)
            greeks = getattr(data, "greeks", None)
            delta = getattr(greeks, "delta", None) if greeks else None
            iv = getattr(data, "implied_volatility", None)
            contracts.append({
                "symbol": sym,
                "ticker": ticker,
                "type": opt_type,
                "strike": strike,
                "expiration": exp_date,
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "delta": delta,
                "iv": iv
            })
        return contracts

    def evaluate_option_position(self, opt: dict, curr_stock_price: float = None):
        contracts = int(opt.get("contracts", 1))
        strike = float(opt.get("strike", 0.0))
        opt_type = opt.get("type", "CALL")
        entry_premium = float(opt.get("entry_premium", 0.0))
        total_cost = float(opt.get("total_cost", entry_premium * 100 * contracts))
        contract_symbol = opt.get("contract_symbol", "")
        
        try:
            exp_date = datetime.strptime(opt.get("expiration", ""), "%Y-%m-%d").date()
        except:
            exp_date = date.today()
            
        today = date.today()
        dte = (exp_date - today).days
        
        bid, ask, mid = self.get_option_quote(contract_symbol)
        curr_premium = mid if mid > 0 else (bid if bid > 0 else ask)
        
        # Fallback to intrinsic value if live quote is 0
        if curr_premium <= 0 and curr_stock_price:
            if opt_type == "CALL":
                curr_premium = max(0.0, curr_stock_price - strike)
            else:
                curr_premium = max(0.0, strike - curr_stock_price)
                
        curr_value = curr_premium * 100 * contracts
        pnl = curr_value - total_cost
        roe = (pnl / total_cost) * 100.0 if total_cost > 0 else 0.0
        
        is_itm = False
        if curr_stock_price:
            is_itm = (curr_stock_price > strike) if opt_type == "CALL" else (curr_stock_price < strike)
            
        return curr_premium, curr_value, pnl, roe, dte, is_itm

    def settle_expired_options(self, user_data: dict, user_id: str = ""):
        options = user_data.get("options", [])
        if not options:
            return []
            
        today = date.today()
        active_options = []
        settlements = []
        
        for opt in list(options):
            try:
                exp_date = datetime.strptime(opt.get("expiration", ""), "%Y-%m-%d").date()
            except:
                active_options.append(opt)
                continue
                
            if exp_date < today:
                # Option has expired!
                symbol = opt.get("symbol", "")
                opt_type = opt.get("type", "CALL")
                strike = float(opt.get("strike", 0.0))
                contracts = int(opt.get("contracts", 1))
                pos_id = opt.get("id", "N/A")
                
                stock_price = 0.0
                try:
                    stock_price = self.get_price(symbol)
                except:
                    pass
                    
                intrinsic = 0.0
                if stock_price > 0:
                    if opt_type == "CALL":
                        intrinsic = max(0.0, stock_price - strike)
                    else:
                        intrinsic = max(0.0, strike - stock_price)
                        
                payout = intrinsic * 100 * contracts
                user_data["cash"] = user_data.get("cash", 0.0) + payout
                
                hist_type = f"EXERCISE {opt_type}" if payout > 0 else f"EXPIRE {opt_type}"
                history = user_data.setdefault("history", [])
                history.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": hist_type,
                    "symbol": f"{symbol} ${strike:,.2f} {opt_type}",
                    "quantity": contracts,
                    "price": intrinsic,
                    "total": payout
                })
                if len(history) > 50:
                    user_data["history"] = history[-50:]
                    
                settlements.append({
                    "id": pos_id,
                    "symbol": symbol,
                    "type": opt_type,
                    "strike": strike,
                    "contracts": contracts,
                    "intrinsic": intrinsic,
                    "payout": payout,
                    "is_itm": payout > 0
                })
            else:
                active_options.append(opt)
                
        user_data["options"] = active_options
        return settlements

    @app_commands.command(name="stonks_help", description="Show full guide and list of all stonks commands.")
    @app_commands.describe(category="Optional category to focus on (Trading, Futures, Options, Portfolio)")
    @app_commands.choices(category=[
        app_commands.Choice(name="All Commands (Overview)", value="all"),
        app_commands.Choice(name="Spot Stock Trading", value="stocks"),
        app_commands.Choice(name="Leveraged Futures Trading", value="futures"),
        app_commands.Choice(name="Options Trading (Calls/Puts)", value="options"),
        app_commands.Choice(name="Portfolio & Leaderboard", value="portfolio"),
    ])
    async def stonks_help(self, interaction: discord.Interaction, category: app_commands.Choice[str] = None):
        selected = category.value if category else "all"
        
        embed = discord.Embed(
            title="📈 UllecBot Stonks Command Guide",
            description=(
                f"Welcome to the virtual stock market trading game! All players start with **${STARTING_CASH:,.2f}** in cash.\n"
                f"Use the commands below to trade live US stocks, leverage futures, and trade real options contracts."
            ),
            color=discord.Color.gold()
        )
        
        if selected in ["all", "stocks"]:
            embed.add_field(
                name="💵 Spot Stock Trading",
                value=(
                    "• `/stonks_join` - Join the competition & claim starting cash\n"
                    "• `/stock <symbol> [period]` - Live price, company info & chart (1W, 1M, 3M, 6M, 1Y)\n"
                    "• `/buy <symbol> <quantity>` - Buy shares of any US stock\n"
                    "• `/buy_random [spend_amount] [quantity]` - Buy a random mystery stock\n"
                    "• `/sell <symbol> <quantity>` - Sell shares you currently own"
                ),
                inline=False
            )
            
        if selected in ["all", "futures"]:
            embed.add_field(
                name="⚡ Leveraged Futures Trading",
                value=(
                    "• `/long <symbol> <margin> [leverage]` - Long contract (profit when stock rises, 2x–50x)\n"
                    "• `/short <symbol> <margin> [leverage]` - Short contract (profit when stock drops, 2x–50x)\n"
                    "• `/close_position <position_id>` - Close active futures contract by ID\n"
                    "• `/positions [user]` - View all open leveraged futures & options"
                ),
                inline=False
            )
            
        if selected in ["all", "options"]:
            embed.add_field(
                name="🎟️ Options Trading (Calls & Puts)",
                value=(
                    "• `/option_chain <symbol> [type] [exp]` - View live option strikes, premiums & ITM/OTM status\n"
                    "• `/buy_call <symbol> <strike> [exp] [contracts]` - Buy Call options (1 contract = 100 shares)\n"
                    "• `/buy_put <symbol> <strike> [exp] [contracts]` - Buy Put options (bearish speculation / hedge)\n"
                    "• `/close_option <position_id>` - Sell option contract back to the market\n"
                    "• `/options_positions [user]` - View active option contracts with Greeks & P/L"
                ),
                inline=False
            )
            
        if selected in ["all", "portfolio"]:
            embed.add_field(
                name="📊 Portfolio & Competition",
                value=(
                    "• `/portfolio [user]` - Full portfolio view, cash, holdings, contracts & net worth\n"
                    "• `/trade_history [user]` - View recent transactions & executions log\n"
                    "• `/leaderboard` - Server rankings by total net worth"
                ),
                inline=False
            )
            
        embed.set_footer(text=f"Commands restricted to #{interaction.channel.name if interaction.channel and hasattr(interaction.channel, 'name') else 'stonks'} • Live Alpaca Market Data")
        await interaction.response.send_message(embed=embed)

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
            "positions": [],
            "options": [],
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

    async def _open_leveraged_position(self, interaction: discord.Interaction, symbol: str, margin: float, leverage: int, pos_type: str):
        if margin <= 0:
            await interaction.response.send_message("Margin must be greater than $0.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        portfolios = self.load_portfolios()

        if user_id not in portfolios:
            await interaction.response.send_message("You haven't joined the competition yet! Use `/stonks_join` to start.", ephemeral=True)
            return

        user_data = portfolios[user_id]
        user_cash = user_data.get("cash", 0.0)

        if margin > user_cash:
            await interaction.response.send_message(f"Insufficient funds! You need **${margin:,.2f}** in margin but only have **${user_cash:,.2f}** cash.", ephemeral=True)
            return

        try:
            entry_price = self.get_price(symbol)
        except Exception as e:
            await interaction.response.send_message(f"Error fetching price for {symbol}: {e}", ephemeral=True)
            return

        if entry_price <= 0:
            await interaction.response.send_message(f"Could not get a valid price for {symbol}.", ephemeral=True)
            return

        notional_value = margin * leverage
        shares = notional_value / entry_price
        
        # Calculate liquidation price
        if pos_type == "LONG":
            liquidation_price = entry_price * (1.0 - (1.0 / leverage))
        else:
            liquidation_price = entry_price * (1.0 + (1.0 / leverage))

        pos_id = str(uuid.uuid4())[:6].upper()
        
        position = {
            "id": pos_id,
            "type": pos_type,
            "symbol": symbol,
            "margin": margin,
            "leverage": leverage,
            "notional": notional_value,
            "shares": shares,
            "entry_price": entry_price,
            "liquidation_price": liquidation_price,
            "opened_at": datetime.now(timezone.utc).isoformat()
        }

        user_data["cash"] -= margin
        positions = user_data.setdefault("positions", [])
        positions.append(position)

        history = user_data.setdefault("history", [])
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": f"OPEN {pos_type} {leverage}x",
            "symbol": symbol,
            "quantity": shares,
            "price": entry_price,
            "total": margin
        })
        if len(history) > 50:
            user_data["history"] = history[-50:]

        self.save_portfolios(portfolios)

        color = discord.Color.green() if pos_type == "LONG" else discord.Color.red()
        emoji = "📈 LONG" if pos_type == "LONG" else "📉 SHORT"

        embed = discord.Embed(
            title=f"⚡ Opened {emoji} Position: {symbol} ({leverage}x)",
            color=color
        )
        embed.add_field(name="🆔 Position ID", value=f"`{pos_id}`", inline=True)
        embed.add_field(name="💵 Entry Price", value=f"${entry_price:,.2f}", inline=True)
        embed.add_field(name="💰 Margin (Collateral)", value=f"${margin:,.2f}", inline=True)
        embed.add_field(name="📊 Position Size (Notional)", value=f"${notional_value:,.2f} ({shares:,.3f} shares)", inline=True)
        embed.add_field(name="⚠️ Liquidation Price", value=f"**${liquidation_price:,.2f}**", inline=True)
        embed.add_field(name="🏦 Remaining Cash", value=f"${user_data['cash']:,.2f}", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="long", description="Open a leveraged LONG position (profit when stock rises).")
    @app_commands.describe(
        symbol="Stock ticker symbol (e.g. NVDA, TSLA, AAPL)",
        margin="Collateral / cash to invest in this contract",
        leverage="Leverage multiplier (2x - 50x, default 5x)"
    )
    @app_commands.choices(leverage=[
        app_commands.Choice(name="2x Leverage", value=2),
        app_commands.Choice(name="3x Leverage", value=3),
        app_commands.Choice(name="5x Leverage", value=5),
        app_commands.Choice(name="10x Leverage", value=10),
        app_commands.Choice(name="20x Leverage", value=20),
        app_commands.Choice(name="50x Leverage", value=50),
    ])
    async def long(self, interaction: discord.Interaction, symbol: str, margin: float, leverage: app_commands.Choice[int] = None):
        await self._open_leveraged_position(interaction, symbol.upper(), margin, leverage.value if leverage else 5, "LONG")

    @app_commands.command(name="short", description="Open a leveraged SHORT position (profit when stock drops).")
    @app_commands.describe(
        symbol="Stock ticker symbol (e.g. NVDA, TSLA, AAPL)",
        margin="Collateral / cash to invest in this contract",
        leverage="Leverage multiplier (2x - 50x, default 5x)"
    )
    @app_commands.choices(leverage=[
        app_commands.Choice(name="2x Leverage", value=2),
        app_commands.Choice(name="3x Leverage", value=3),
        app_commands.Choice(name="5x Leverage", value=5),
        app_commands.Choice(name="10x Leverage", value=10),
        app_commands.Choice(name="20x Leverage", value=20),
        app_commands.Choice(name="50x Leverage", value=50),
    ])
    async def short(self, interaction: discord.Interaction, symbol: str, margin: float, leverage: app_commands.Choice[int] = None):
        await self._open_leveraged_position(interaction, symbol.upper(), margin, leverage.value if leverage else 5, "SHORT")

    @app_commands.command(name="close_position", description="Close an open leveraged Long or Short contract.")
    @app_commands.describe(position_id="The ID of the position to close (e.g. 8A3F12)")
    async def close_position(self, interaction: discord.Interaction, position_id: str):
        position_id = position_id.strip().upper()
        user_id = str(interaction.user.id)
        portfolios = self.load_portfolios()

        if user_id not in portfolios:
            await interaction.response.send_message("You haven't joined the competition yet!", ephemeral=True)
            return

        user_data = portfolios[user_id]
        positions = user_data.get("positions", [])
        
        target_pos = None
        target_idx = -1
        for idx, p in enumerate(positions):
            if p.get("id", "").upper() == position_id:
                target_pos = p
                target_idx = idx
                break

        if not target_pos:
            await interaction.response.send_message(f"No open position found with ID `{position_id}`. Use `/positions` to see your active contracts.", ephemeral=True)
            return

        symbol = target_pos["symbol"]
        try:
            curr_price = self.get_price(symbol)
        except Exception as e:
            await interaction.response.send_message(f"Error fetching current price for {symbol}: {e}", ephemeral=True)
            return

        is_liq, pnl, return_amount, roe = self.evaluate_contract(target_pos, curr_price)
        
        positions.pop(target_idx)
        user_data["cash"] += return_amount

        history = user_data.setdefault("history", [])
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": f"CLOSE {target_pos['type']} (LIQ)" if is_liq else f"CLOSE {target_pos['type']}",
            "symbol": symbol,
            "quantity": target_pos["shares"],
            "price": curr_price,
            "total": return_amount
        })
        if len(history) > 50:
            user_data["history"] = history[-50:]

        self.save_portfolios(portfolios)

        sign = "+" if pnl >= 0 else ""
        roe_sign = "+" if roe >= 0 else ""
        color = discord.Color.red() if is_liq or pnl < 0 else discord.Color.green()

        if is_liq:
            embed = discord.Embed(
                title=f"💥 Position Liquidated: {target_pos['type']} {symbol} (`{position_id}`)",
                description=f"Market price hit **${curr_price:,.2f}** (Liquidation: **${target_pos['liquidation_price']:,.2f}**). All collateral (${target_pos['margin']:,.2f}) was lost.",
                color=discord.Color.dark_red()
            )
        else:
            embed = discord.Embed(
                title=f"🔒 Closed Position: {target_pos['type']} {symbol} (`{position_id}`)",
                color=color
            )
            embed.add_field(name="💵 Entry → Exit", value=f"${target_pos['entry_price']:,.2f} → ${curr_price:,.2f}", inline=True)
            embed.add_field(name="📊 P/L & ROE", value=f"**{sign}${pnl:,.2f} ({roe_sign}{roe:.2f}%)**", inline=True)
            embed.add_field(name="💰 Returned Cash", value=f"**${return_amount:,.2f}**", inline=True)
            embed.add_field(name="🏦 New Cash Balance", value=f"${user_data['cash']:,.2f}", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="option_chain", description="View live options chain (calls/puts, strikes, premiums, and Greeks).")
    @app_commands.describe(
        symbol="Stock ticker symbol (e.g. AAPL, NVDA, TSLA)",
        option_type="CALL (bullish) or PUT (bearish)",
        expiration="Expiration date (YYYY-MM-DD, e.g. 2026-08-31). Defaults to nearest."
    )
    @app_commands.choices(option_type=[
        app_commands.Choice(name="CALL (Buy Right to Purchase)", value="CALL"),
        app_commands.Choice(name="PUT (Buy Right to Sell)", value="PUT"),
    ])
    async def option_chain(self, interaction: discord.Interaction, symbol: str, option_type: app_commands.Choice[str] = None, expiration: str = None):
        await interaction.response.defer()
        symbol = symbol.strip().upper()
        selected_type = option_type.value if option_type else "CALL"
        
        try:
            curr_stock_price = self.get_price(symbol)
        except Exception as e:
            await interaction.followup.send(f"Error fetching stock price for **{symbol}**: {e}", ephemeral=True)
            return
            
        try:
            contracts = self.get_option_chain_data(symbol)
        except Exception as e:
            await interaction.followup.send(f"Error fetching option chain for **{symbol}**: {e}", ephemeral=True)
            return
            
        if not contracts:
            await interaction.followup.send(f"No option contracts found for **{symbol}**.", ephemeral=True)
            return
            
        today = date.today()
        upcoming_expirations = sorted(list(set(c["expiration"] for c in contracts if c["expiration"] >= today)))
        if not upcoming_expirations:
            await interaction.followup.send(f"No active unexpired option contracts found for **{symbol}**.", ephemeral=True)
            return
            
        target_exp = upcoming_expirations[0]
        if expiration:
            try:
                parsed_exp = datetime.strptime(expiration.strip(), "%Y-%m-%d").date()
                if parsed_exp in upcoming_expirations:
                    target_exp = parsed_exp
                else:
                    target_exp = min(upcoming_expirations, key=lambda d: abs((d - parsed_exp).days))
            except Exception:
                await interaction.followup.send(f"Invalid expiration format `{expiration}`. Please use `YYYY-MM-DD`.", ephemeral=True)
                return

        type_contracts = [c for c in contracts if c["expiration"] == target_exp and c["type"] == selected_type]
        if not type_contracts:
            await interaction.followup.send(f"No {selected_type} contracts found for expiration `{target_exp}`.", ephemeral=True)
            return
            
        type_contracts.sort(key=lambda x: x["strike"])
        
        # Find index closest to curr_stock_price
        closest_idx = 0
        min_diff = float("inf")
        for i, c in enumerate(type_contracts):
            diff = abs(c["strike"] - curr_stock_price)
            if diff < min_diff:
                min_diff = diff
                closest_idx = i
                
        # Take 8 strikes centered around ATM
        start_idx = max(0, closest_idx - 4)
        end_idx = min(len(type_contracts), start_idx + 9)
        selected_slice = type_contracts[start_idx:end_idx]
        
        type_emoji = "📈 CALL" if selected_type == "CALL" else "📉 PUT"
        color = discord.Color.green() if selected_type == "CALL" else discord.Color.red()
        dte = (target_exp - today).days
        
        embed = discord.Embed(
            title=f"📊 {symbol} Options Chain • {type_emoji}",
            description=f"**Stock Price:** `${curr_stock_price:,.2f}` | **Expiration:** `{target_exp.strftime('%b %d, %Y')}` ({dte} DTE)\n*1 Contract = 100 Shares*",
            color=color
        )
        
        lines = []
        lines.append("` Strike  |  Bid   |  Ask   |  Mid   | $/Contr | ITM/OTM `")
        lines.append("`" + "-" * 51 + "`")
        
        for c in selected_slice:
            strike = c["strike"]
            bid = c["bid"]
            ask = c["ask"]
            mid = c["mid"]
            cost_per_contract = (ask if ask > 0 else mid) * 100
            
            is_itm = (curr_stock_price >= strike) if selected_type == "CALL" else (curr_stock_price <= strike)
            status = "🟢 ITM" if is_itm else "⚪ OTM"
            if abs(strike - curr_stock_price) == min_diff:
                status += " (ATM)"
                
            line = f"` ${strike:>6.2f} | ${bid:>5.2f} | ${ask:>5.2f} | ${mid:>5.2f} | ${cost_per_contract:>7.2f} | {status:<10} `"
            lines.append(line)
            
        embed.add_field(name="📋 Available Strikes & Premiums", value="\n".join(lines), inline=False)
        
        other_exps = [d.strftime("%Y-%m-%d") for d in upcoming_expirations[:6]]
        cmd_name = "/buy_call" if selected_type == "CALL" else "/buy_put"
        embed.set_footer(text=f"Other Expirations: {', '.join(other_exps)} | Use {cmd_name} to trade")
        
        await interaction.followup.send(embed=embed)

    async def _buy_option_contract(self, interaction: discord.Interaction, symbol: str, opt_type: str, strike: float, expiration: str = None, contracts: int = 1):
        if contracts <= 0:
            await interaction.response.send_message("Number of contracts must be at least 1.", ephemeral=True)
            return
            
        symbol = symbol.strip().upper()
        user_id = str(interaction.user.id)
        portfolios = self.load_portfolios()
        
        if user_id not in portfolios:
            await interaction.response.send_message("You haven't joined the competition yet! Use `/stonks_join` to start.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        user_data = portfolios[user_id]
        user_cash = user_data.get("cash", 0.0)
        
        try:
            curr_stock_price = self.get_price(symbol)
        except Exception as e:
            await interaction.followup.send(f"Error fetching stock price for {symbol}: {e}", ephemeral=True)
            return
            
        try:
            chain = self.get_option_chain_data(symbol)
        except Exception as e:
            await interaction.followup.send(f"Error fetching options chain for {symbol}: {e}", ephemeral=True)
            return
            
        if not chain:
            await interaction.followup.send(f"No option contracts found for **{symbol}**.", ephemeral=True)
            return
            
        today = date.today()
        upcoming_expirations = sorted(list(set(c["expiration"] for c in chain if c["expiration"] >= today)))
        if not upcoming_expirations:
            await interaction.followup.send(f"No active unexpired option contracts available for **{symbol}**.", ephemeral=True)
            return
            
        target_exp = upcoming_expirations[0]
        if expiration and expiration.strip().lower() != "nearest":
            try:
                parsed_exp = datetime.strptime(expiration.strip(), "%Y-%m-%d").date()
                if parsed_exp in upcoming_expirations:
                    target_exp = parsed_exp
                else:
                    target_exp = min(upcoming_expirations, key=lambda d: abs((d - parsed_exp).days))
            except Exception:
                await interaction.followup.send(f"Invalid expiration date format `{expiration}`. Please use `YYYY-MM-DD`.", ephemeral=True)
                return
                
        matching = [c for c in chain if c["expiration"] == target_exp and c["type"] == opt_type]
        if not matching:
            await interaction.followup.send(f"No {opt_type} contracts found for expiration `{target_exp}`.", ephemeral=True)
            return
            
        closest_contract = min(matching, key=lambda c: abs(c["strike"] - strike))
        actual_strike = closest_contract["strike"]
        
        ask = closest_contract["ask"]
        mid = closest_contract["mid"]
        bid = closest_contract["bid"]
        exec_premium = ask if ask > 0 else (mid if mid > 0 else bid)
        
        if exec_premium <= 0:
            await interaction.followup.send(f"Could not get a valid market ask/premium for **{closest_contract['symbol']}**.", ephemeral=True)
            return
            
        cost_per_contract = exec_premium * 100.0
        total_cost = cost_per_contract * contracts
        
        if total_cost > user_cash:
            await interaction.followup.send(
                f"Insufficient funds! You need **${total_cost:,.2f}** ({contracts} contract(s) @ ${exec_premium:,.2f}/share) but only have **${user_cash:,.2f}** cash.",
                ephemeral=True
            )
            return
            
        pos_id = "OPT-" + str(uuid.uuid4())[:6].upper()
        contract_symbol = closest_contract["symbol"]
        
        opt_pos = {
            "id": pos_id,
            "symbol": symbol,
            "contract_symbol": contract_symbol,
            "type": opt_type,
            "strike": actual_strike,
            "expiration": str(target_exp),
            "contracts": contracts,
            "entry_premium": exec_premium,
            "total_cost": total_cost,
            "opened_at": datetime.now(timezone.utc).isoformat()
        }
        
        user_data["cash"] -= total_cost
        user_options = user_data.setdefault("options", [])
        user_options.append(opt_pos)
        
        history = user_data.setdefault("history", [])
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": f"BUY {opt_type}",
            "symbol": f"{symbol} ${actual_strike:,.2f} {opt_type} ({target_exp})",
            "quantity": contracts,
            "price": exec_premium,
            "total": total_cost
        })
        if len(history) > 50:
            user_data["history"] = history[-50:]
            
        self.save_portfolios(portfolios)
        
        if opt_type == "CALL":
            breakeven = actual_strike + exec_premium
        else:
            breakeven = actual_strike - exec_premium
            
        dte = (target_exp - today).days
        color = discord.Color.green() if opt_type == "CALL" else discord.Color.red()
        emoji = "📈 CALL" if opt_type == "CALL" else "📉 PUT"
        
        embed = discord.Embed(
            title=f"🎟️ Purchased {contracts:,}x {symbol} ${actual_strike:,.2f} {emoji}",
            description=f"Contract: `{contract_symbol}`\nExpiration: `{target_exp.strftime('%b %d, %Y')}` ({dte} days)",
            color=color
        )
        embed.add_field(name="💵 Premium (per share)", value=f"${exec_premium:,.2f}", inline=True)
        embed.add_field(name="🧾 Total Cost", value=f"${total_cost:,.2f}", inline=True)
        embed.add_field(name="🎯 Breakeven Stock Price", value=f"**${breakeven:,.2f}**", inline=True)
        embed.add_field(name="🆔 Position ID", value=f"`{pos_id}`", inline=True)
        embed.add_field(name="🛡️ Max Risk / Loss", value=f"${total_cost:,.2f} (100% of premium)", inline=True)
        embed.add_field(name="💰 Remaining Cash", value=f"${user_data['cash']:,.2f}", inline=True)
        embed.set_footer(text=f"Use /close_option position_id:{pos_id} to sell this contract back to the market.")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="buy_call", description="Buy Call option contracts (bullish speculation / leverage).")
    @app_commands.describe(
        symbol="Stock ticker symbol (e.g. AAPL, NVDA, TSLA)",
        strike="Strike price (e.g. 230)",
        expiration="Expiration date (YYYY-MM-DD, e.g. 2026-08-31). Defaults to nearest.",
        contracts="Number of option contracts (1 contract = 100 shares, default 1)"
    )
    async def buy_call(self, interaction: discord.Interaction, symbol: str, strike: float, expiration: str = None, contracts: int = 1):
        await self._buy_option_contract(interaction, symbol, "CALL", strike, expiration, contracts)

    @app_commands.command(name="buy_put", description="Buy Put option contracts (bearish speculation / hedge).")
    @app_commands.describe(
        symbol="Stock ticker symbol (e.g. AAPL, NVDA, TSLA)",
        strike="Strike price (e.g. 230)",
        expiration="Expiration date (YYYY-MM-DD, e.g. 2026-08-31). Defaults to nearest.",
        contracts="Number of option contracts (1 contract = 100 shares, default 1)"
    )
    async def buy_put(self, interaction: discord.Interaction, symbol: str, strike: float, expiration: str = None, contracts: int = 1):
        await self._buy_option_contract(interaction, symbol, "PUT", strike, expiration, contracts)

    @app_commands.command(name="close_option", description="Sell an active options contract back to the market.")
    @app_commands.describe(position_id="The Position ID of the option to close (e.g. OPT-7B29)")
    async def close_option(self, interaction: discord.Interaction, position_id: str):
        await interaction.response.defer()
        position_id = position_id.strip().upper()
        if not position_id.startswith("OPT-") and len(position_id) == 6:
            position_id = "OPT-" + position_id
            
        user_id = str(interaction.user.id)
        portfolios = self.load_portfolios()
        
        if user_id not in portfolios:
            await interaction.followup.send("You haven't joined the competition yet!", ephemeral=True)
            return
            
        user_data = portfolios[user_id]
        options = user_data.get("options", [])
        
        target_opt = None
        target_idx = -1
        for idx, opt in enumerate(options):
            if opt.get("id", "").upper() == position_id:
                target_opt = opt
                target_idx = idx
                break
                
        if not target_opt:
            await interaction.followup.send(f"No open option contract found with ID `{position_id}`. Use `/options_positions` to see your active contracts.", ephemeral=True)
            return
            
        symbol = target_opt["symbol"]
        contracts = int(target_opt.get("contracts", 1))
        entry_premium = float(target_opt.get("entry_premium", 0.0))
        opt_type = target_opt.get("type", "CALL")
        strike = float(target_opt.get("strike", 0.0))
        
        curr_stock_price = None
        try:
            curr_stock_price = self.get_price(symbol)
        except:
            pass
            
        curr_premium, curr_value, pnl, roe, dte, is_itm = self.evaluate_option_position(target_opt, curr_stock_price)
        
        options.pop(target_idx)
        user_data["cash"] += curr_value
        
        history = user_data.setdefault("history", [])
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": f"CLOSE {opt_type}",
            "symbol": f"{symbol} ${strike:,.2f} {opt_type}",
            "quantity": contracts,
            "price": curr_premium,
            "total": curr_value
        })
        if len(history) > 50:
            user_data["history"] = history[-50:]
            
        self.save_portfolios(portfolios)
        
        sign = "+" if pnl >= 0 else ""
        roe_sign = "+" if roe >= 0 else ""
        color = discord.Color.green() if pnl >= 0 else discord.Color.red()
        emoji = "📈 CALL" if opt_type == "CALL" else "📉 PUT"
        
        embed = discord.Embed(
            title=f"🔒 Closed Option: {symbol} ${strike:,.2f} {emoji} (`{position_id}`)",
            color=color
        )
        embed.add_field(name="💵 Premium Entry → Exit", value=f"${entry_premium:,.2f} → ${curr_premium:,.2f}", inline=True)
        embed.add_field(name="📊 P/L & ROE", value=f"**{sign}${pnl:,.2f} ({roe_sign}{roe:.2f}%)**", inline=True)
        embed.add_field(name="💰 Returned Proceeds", value=f"**${curr_value:,.2f}**", inline=True)
        embed.add_field(name="🏦 New Cash Balance", value=f"${user_data['cash']:,.2f}", inline=True)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="options_positions", description="View your or another user's open options contracts.")
    @app_commands.describe(user="The user whose options you want to view (defaults to yourself)")
    async def options_positions(self, interaction: discord.Interaction, user: discord.Member = None):
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
        
        settlements = self.settle_expired_options(user_data, user_id)
        if settlements:
            self.save_portfolios(portfolios)
            
        options = user_data.get("options", [])
        if not options:
            name_ref = f"**{target_user.display_name}** has" if user and user != interaction.user else "You have"
            await interaction.followup.send(f"{name_ref} no open options contracts! Use `/buy_call` or `/buy_put` to open one.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title=f"📜 {target_user.display_name}'s Open Options Contracts",
            color=discord.Color.purple()
        )
        
        total_cost = 0.0
        total_curr_val = 0.0
        
        for opt in list(options):
            pos_id = opt.get("id", "N/A")
            symbol = opt.get("symbol", "N/A")
            opt_type = opt.get("type", "CALL")
            strike = float(opt.get("strike", 0.0))
            contracts = int(opt.get("contracts", 1))
            entry_premium = float(opt.get("entry_premium", 0.0))
            cost = float(opt.get("total_cost", entry_premium * 100 * contracts))
            exp_str = opt.get("expiration", "")
            
            curr_stock_price = None
            try:
                curr_stock_price = self.get_price(symbol)
            except:
                pass
                
            curr_premium, curr_val, pnl, roe, dte, is_itm = self.evaluate_option_position(opt, curr_stock_price)
            
            total_cost += cost
            total_curr_val += curr_val
            
            emoji = "📈" if opt_type == "CALL" else "📉"
            status_itm = "🟢 ITM" if is_itm else "⚪ OTM"
            pnl_sign = "+" if pnl >= 0 else ""
            roe_sign = "+" if roe >= 0 else ""
            
            stock_info = f" (Stock: ${curr_stock_price:,.2f})" if curr_stock_price else ""
            
            embed.add_field(
                name=f"{emoji} {symbol} ${strike:,.2f} {opt_type} ({contracts}x) • `{pos_id}`",
                value=(
                    f"Expiration: `{exp_str}` ({dte} DTE) | Status: {status_itm}{stock_info}\n"
                    f"Premium: **${entry_premium:,.2f}** → **${curr_premium:,.2f}** (Cost: ${cost:,.2f} → Value: **${curr_val:,.2f}**)\n"
                    f"P/L: **{pnl_sign}${pnl:,.2f} ({roe_sign}{roe:.2f}%)**"
                ),
                inline=False
            )
            
        total_pnl = total_curr_val - total_cost
        pnl_sign = "+" if total_pnl >= 0 else ""
        embed.set_footer(text=f"Total Option Value: ${total_curr_val:,.2f} | Total Unrealized P/L: {pnl_sign}${total_pnl:,.2f}")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="positions", description="View open leveraged futures and option contracts.")
    @app_commands.describe(user="The user whose positions you want to view (defaults to yourself)")
    async def positions(self, interaction: discord.Interaction, user: discord.Member = None):
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
        
        settlements = self.settle_expired_options(user_data, user_id)
        if settlements:
            self.save_portfolios(portfolios)
            
        active_positions = user_data.get("positions", [])
        options = user_data.get("options", [])
        
        if not active_positions and not options:
            name_ref = f"**{target_user.display_name}** has" if user and user != interaction.user else "You have"
            await interaction.followup.send(f"{name_ref} no open futures or option positions!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"⚡ {target_user.display_name}'s Open Positions",
            color=discord.Color.purple()
        )

        total_margin = 0.0
        total_pnl = 0.0
        
        for pos in list(active_positions):
            symbol = pos["symbol"]
            pos_id = pos["id"]
            pos_type = pos["type"]
            leverage = pos["leverage"]
            margin = pos["margin"]
            entry_price = pos["entry_price"]
            liq_price = pos["liquidation_price"]
            
            try:
                curr_price = self.get_price(symbol)
                is_liq, pnl, equity, roe = self.evaluate_contract(pos, curr_price)
                
                total_margin += margin
                total_pnl += pnl
                
                emoji = "📈" if pos_type == "LONG" else "📉"
                pnl_sign = "+" if pnl >= 0 else ""
                roe_sign = "+" if roe >= 0 else ""
                
                status_text = "💥 **LIQUIDATED**" if is_liq else f"**{pnl_sign}${pnl:,.2f} ({roe_sign}{roe:.2f}%)**"
                
                embed.add_field(
                    name=f"{emoji} Futures: {pos_type} {symbol} ({leverage}x) • `{pos_id}`",
                    value=(
                        f"Entry: **${entry_price:,.2f}** | Now: **${curr_price:,.2f}**\n"
                        f"Margin: **${margin:,.2f}** | Liq Price: **${liq_price:,.2f}**\n"
                        f"P/L: {status_text}"
                    ),
                    inline=False
                )
            except Exception:
                embed.add_field(
                    name=f"⚠️ Futures: {pos_type} {symbol} ({leverage}x) • `{pos_id}`",
                    value=f"Margin: **${margin:,.2f}** (Live price unavailable)",
                    inline=False
                )
                
        for opt in list(options):
            pos_id = opt.get("id", "N/A")
            symbol = opt.get("symbol", "N/A")
            opt_type = opt.get("type", "CALL")
            strike = float(opt.get("strike", 0.0))
            contracts = int(opt.get("contracts", 1))
            entry_premium = float(opt.get("entry_premium", 0.0))
            cost = float(opt.get("total_cost", entry_premium * 100 * contracts))
            exp_str = opt.get("expiration", "")
            
            curr_stock_price = None
            try:
                curr_stock_price = self.get_price(symbol)
            except:
                pass
                
            curr_premium, curr_val, pnl, roe, dte, is_itm = self.evaluate_option_position(opt, curr_stock_price)
            total_pnl += pnl
            
            emoji = "📈" if opt_type == "CALL" else "📉"
            status_itm = "🟢 ITM" if is_itm else "⚪ OTM"
            pnl_sign = "+" if pnl >= 0 else ""
            roe_sign = "+" if roe >= 0 else ""
            
            embed.add_field(
                name=f"{emoji} Option: {symbol} ${strike:,.2f} {opt_type} ({contracts}x) • `{pos_id}`",
                value=(
                    f"Expiration: `{exp_str}` ({dte} DTE) | Status: {status_itm}\n"
                    f"Premium: **${entry_premium:,.2f}** → **${curr_premium:,.2f}** (Value: **${curr_val:,.2f}**)\n"
                    f"P/L: **{pnl_sign}${pnl:,.2f} ({roe_sign}{roe:.2f}%)**"
                ),
                inline=False
            )

        pnl_sign = "+" if total_pnl >= 0 else ""
        embed.set_footer(text=f"Total Unrealized P/L: {pnl_sign}${total_pnl:,.2f}")
        await interaction.followup.send(embed=embed)

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
        
        settlements = self.settle_expired_options(user_data, user_id)
        if settlements:
            self.save_portfolios(portfolios)
            
        cash = user_data.get("cash", 0.0)
        holdings = user_data.get("holdings", {})
        positions = user_data.get("positions", [])
        options = user_data.get("options", [])
        
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
                
        positions_text = "\n".join(holdings_lines) if holdings_lines else "No active spot holdings."
        
        # Calculate futures / positions value
        total_futures_equity = 0.0
        futures_lines = []
        for pos in positions:
            p_sym = pos.get("symbol", "N/A")
            p_type = pos.get("type", "LONG")
            p_lev = pos.get("leverage", 1)
            p_id = pos.get("id", "N/A")
            p_margin = pos.get("margin", 0.0)
            try:
                p_price = self.get_price(p_sym)
                is_liq, p_pnl, p_eq, p_roe = self.evaluate_contract(pos, p_price)
                total_futures_equity += p_eq
                p_emoji = "📈" if p_type == "LONG" else "📉"
                p_sign = "+" if p_pnl >= 0 else ""
                futures_lines.append(f"{p_emoji} `{p_id}` **{p_type} {p_sym}** ({p_lev}x): Margin **${p_margin:,.2f}** → Equity **${p_eq:,.2f}** ({p_sign}${p_pnl:,.2f})")
            except:
                total_futures_equity += p_margin
                futures_lines.append(f"⚡ `{p_id}` **{p_type} {p_sym}** ({p_lev}x): Margin **${p_margin:,.2f}**")

        # Calculate options value
        total_options_value = 0.0
        options_lines = []
        for opt in options:
            o_sym = opt.get("symbol", "N/A")
            o_type = opt.get("type", "CALL")
            o_strike = float(opt.get("strike", 0.0))
            o_contracts = int(opt.get("contracts", 1))
            o_id = opt.get("id", "N/A")
            o_exp = opt.get("expiration", "")
            
            curr_stk = None
            try:
                curr_stk = self.get_price(o_sym)
            except:
                pass
                
            o_prem, o_val, o_pnl, o_roe, o_dte, o_itm = self.evaluate_option_position(opt, curr_stk)
            total_options_value += o_val
            o_emoji = "📈" if o_type == "CALL" else "📉"
            o_sign = "+" if o_pnl >= 0 else ""
            options_lines.append(f"{o_emoji} `{o_id}` **{o_sym} ${o_strike:,.2f} {o_type}** ({o_contracts}x, exp `{o_exp}`): Value **${o_val:,.2f}** ({o_sign}${o_pnl:,.2f})")

        net_worth = cash + total_holdings_value + total_futures_equity + total_options_value
        total_return = net_worth - STARTING_CASH
        total_return_pct = (total_return / STARTING_CASH) * 100
        return_sign = "+" if total_return >= 0 else ""
        return_emoji = "📈" if total_return >= 0 else "📉"
        
        embed_color = discord.Color.green() if total_return >= 0 else discord.Color.red()
        embed = discord.Embed(title=f"📊 {target_user.display_name}'s Portfolio", color=embed_color)
        
        embed.add_field(name="💰 Cash Balance", value=f"${cash:,.2f}", inline=True)
        embed.add_field(name="📦 Spot Holdings Value", value=f"${total_holdings_value:,.2f}", inline=True)
        if positions:
            embed.add_field(name="⚡ Futures Contracts Equity", value=f"${total_futures_equity:,.2f}", inline=True)
        if options:
            embed.add_field(name="📜 Options Value", value=f"${total_options_value:,.2f}", inline=True)
            
        embed.add_field(name="💎 Total Net Worth", value=f"**${net_worth:,.2f}**", inline=False)
        embed.add_field(name=f"{return_emoji} Total Overall Return", value=f"**{return_sign}${total_return:,.2f} ({return_sign}{total_return_pct:.2f}%)**", inline=False)
        embed.add_field(name="📦 Spot Holdings", value=positions_text, inline=False)
        
        if futures_lines:
            embed.add_field(name="⚡ Open Futures Positions", value="\n".join(futures_lines), inline=False)
            
        if options_lines:
            embed.add_field(name="📜 Open Option Contracts", value="\n".join(options_lines), inline=False)
        
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
            emoji = "🟢" if "BUY" in ttype or "LONG" in ttype or "EXERCISE" in ttype else "🔴"
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
                name=f"{emoji} {ttype} • {sym} @ ${prc:,.2f}",
                value=f"Amount: **${tot:,.2f}** ({qty} qty) • *{time_str}*",
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
                        
            # Add open futures positions equity
            for pos in data.get("positions", []):
                try:
                    p_price = self.get_price(pos["symbol"])
                    _, _, eq, _ = self.evaluate_contract(pos, p_price)
                    total_value += eq
                except:
                    total_value += pos.get("margin", 0.0)
                    
            # Add open options positions equity
            for opt in data.get("options", []):
                try:
                    curr_stk = self.get_price(opt.get("symbol", ""))
                except:
                    curr_stk = None
                try:
                    _, o_val, _, _, _, _ = self.evaluate_option_position(opt, curr_stk)
                    total_value += o_val
                except:
                    total_value += opt.get("total_cost", 0.0)
                    
            leaderboard_data.append((uid, total_value))
            
        leaderboard_data.sort(key=lambda x: x[1], reverse=True)
        
        embed = discord.Embed(title="🏆 Stonks Leaderboard", color=discord.Color.gold())
        
        for i, (uid, net_worth) in enumerate(leaderboard_data[:10]):
            member = interaction.guild.get_member(int(uid))
            name = member.display_name if member else f"User {uid}"
            
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
