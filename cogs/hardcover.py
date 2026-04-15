import discord
from discord import app_commands
from discord.ext import commands
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio
import os
import json
from datetime import datetime, timedelta


class hardcoverCog(commands.Cog, name="hardcover"):
    def __init__(self, bot):
        self.bot = bot
        
        token = os.environ.get('hardcover_token', '')
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            with open(os.path.join(base_dir, 'configs', 'hardcover_token.json'), 'r') as f:
                data = json.load(f)
                token = data.get('token', token)
        except Exception as e:
            print(f"Failed to load hardcover_token: {e}")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "UllecBot/1.0 (Discord Bot)"
        }
        transport = AIOHTTPTransport(url="https://api.hardcover.app/v1/graphql", headers=headers)
        self.client = Client(transport=transport)



    @app_commands.command(name="register", description="Register your Hardcover username")
    @app_commands.describe(username="Your Hardcover username or ID")
    async def register(self, interaction: discord.Interaction, username: str):
        user_file = 'db/hardcover_users.json'
        users = {}
        
        # Load existing users if the file exists
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    users = json.load(f)
            except json.JSONDecodeError:
                pass
                
        users[str(interaction.user.id)] = username
        
        with open(user_file, 'w') as f:
            json.dump(users, f, indent=4)
            
        await interaction.response.send_message(f"Successfully registered your Hardcover username as `{username}`!", ephemeral=True)

    @app_commands.command(name="readlist", description="Show your Hardcover read list")
    @app_commands.describe(username="Optional Hardcover username to lookup instead of your own")
    async def readlist(self, interaction: discord.Interaction, username: str = None):
        await interaction.response.defer()
        
        user_file = 'db/hardcover_users.json'
        users = {}
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    users = json.load(f)
            except json.JSONDecodeError:
                pass
                
        if username:
            identifier = username
        else:
            identifier = users.get(str(interaction.user.id))
        
        if not identifier:
            await interaction.followup.send("You haven't registered a Hardcover username yet! Use `/register` first.", ephemeral=True)
            return

        is_id = identifier.isdigit()
        
        if is_id:
            query_str = """
            query GetUserBooks($id: Int!) {
                users(where: {id: {_eq: $id}}, limit: 1) {
                    id
                    username
                    name
                    user_books(where: {status_id: {_eq: 3}}, limit: 50, order_by: {rating: desc_nulls_last}) {
                        rating
                        book {
                            title
                            contributions(limit: 1) {
                                author {
                                    name
                                }
                            }
                        }
                    }
                }
            }
            """
            params = {"id": int(identifier)}
        else:
            query_str = """
            query GetUserBooks($username: citext!) {
                users(where: {username: {_eq: $username}}, limit: 1) {
                    id
                    username
                    name
                    user_books(where: {status_id: {_eq: 3}}, limit: 50, order_by: {rating: desc_nulls_last}) {
                        rating
                        book {
                            title
                            contributions(limit: 1) {
                                author {
                                    name
                                }
                            }
                        }
                    }
                }
            }
            """
            params = {"username": identifier}

        try:
            query = gql(query_str)
            
            async with self.client as session:
                result = await session.execute(query, variable_values=params)
            
            users_data = result.get("users", [])
            if not users_data:
                await interaction.followup.send(f"Could not find a Hardcover user matching `{identifier}`.")
                return
            
            user = users_data[0]
            username = user.get("username") or user.get("name") or identifier
            user_books = user.get("user_books", [])
            
            if not user_books:
                await interaction.followup.send(f"**{username}** has no books in their read list.")
                return
            
            embed = discord.Embed(title=f"{username}'s Read List", color=discord.Color.blue())
            embed.set_footer(text="Powered by Hardcover API")
            
            books_text = ""
            for ub in user_books:
                book = ub.get("book") or {}
                title = book.get("title", "Unknown Book")
                rating = ub.get("rating")
                
                author_name = ""
                contribs = book.get("contributions") or []
                if contribs:
                    author = contribs[0].get("author") or {}
                    author_name = author.get("name", "")
                
                rating_str = f" ({rating}⭐)" if rating is not None else ""
                
                if author_name:
                    line = f"• **{title}** by {author_name}{rating_str}\n"
                else:
                    line = f"• **{title}**{rating_str}\n"
                    
                if len(books_text) + len(line) > 4000:
                    books_text += "• *...and more*\n"
                    break
                books_text += line
                    
            embed.description = books_text
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching the read list:\n```\n{e}\n```")

    @app_commands.command(name="readinglist", description="Show your Hardcover currently reading list")
    async def readinglist(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user_file = 'db/hardcover_users.json'
        users = {}
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    users = json.load(f)
            except json.JSONDecodeError:
                pass
                
        identifier = users.get(str(interaction.user.id))
        
        if not identifier:
            await interaction.followup.send("You haven't registered a Hardcover username yet! Use `/register` first.", ephemeral=True)
            return

        is_id = identifier.isdigit()
        
        if is_id:
            query_str = """
            query GetUserBooks($id: Int!) {
                users(where: {id: {_eq: $id}}, limit: 1) {
                    id
                    username
                    name
                    user_books(where: {status_id: {_eq: 2}}, limit: 10, order_by: {updated_at: desc}) {
                        book {
                            title
                            contributions(limit: 1) {
                                author {
                                    name
                                }
                            }
                        }
                    }
                }
            }
            """
            params = {"id": int(identifier)}
        else:
            query_str = """
            query GetUserBooks($username: citext!) {
                users(where: {username: {_eq: $username}}, limit: 1) {
                    id
                    username
                    name
                    user_books(where: {status_id: {_eq: 2}}, limit: 10, order_by: {updated_at: desc}) {
                        book {
                            title
                            contributions(limit: 1) {
                                author {
                                    name
                                }
                            }
                        }
                    }
                }
            }
            """
            params = {"username": identifier}

        try:
            query = gql(query_str)
            
            async with self.client as session:
                result = await session.execute(query, variable_values=params)
            
            users_data = result.get("users", [])
            if not users_data:
                await interaction.followup.send(f"Could not find a Hardcover user matching `{identifier}`.")
                return
            
            user = users_data[0]
            username = user.get("username") or user.get("name") or identifier
            user_books = user.get("user_books", [])
            
            if not user_books:
                await interaction.followup.send(f"**{username}** is not currently reading any books.")
                return
            
            embed = discord.Embed(title=f"{username}'s Currently Reading List", color=discord.Color.green())
            embed.set_footer(text="Powered by Hardcover API")
            
            books_text = ""
            for ub in user_books:
                book = ub.get("book") or {}
                title = book.get("title", "Unknown Book")
                
                author_name = ""
                contribs = book.get("contributions") or []
                if contribs:
                    author = contribs[0].get("author") or {}
                    author_name = author.get("name", "")
                
                if author_name:
                    books_text += f"• **{title}** by {author_name}\n"
                else:
                    books_text += f"• **{title}**\n"
                    
            embed.description = books_text
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching the currently reading list:\n```\n{e}\n```")

    @app_commands.command(name="trending", description="Show top 5 trending books for the last month on Hardcover")
    async def trending(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        since_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        query_str = """
        query GetTrendingBooks {
            books(limit: 5, order_by: {ratings_count: desc_nulls_last}, where: {release_date: {_gte: "%s"}}) {
                title
                rating
                contributions(limit: 1) {
                    author {
                        name
                    }
                }
            }
        }""" % since_date
        
        try:
            query = gql(query_str)
            
            async with self.client as session:
                result = await session.execute(query)
            
            books_data = result.get("books", [])
            
            if not books_data:
                await interaction.followup.send("Could not fetch trending books from Hardcover.")
                return
            
            embed = discord.Embed(title="Hardcover's Top 5 Trending Books (Last Month)", color=discord.Color.gold())
            embed.set_footer(text="Powered by Hardcover API")
            
            books_text = ""
            for book in books_data:
                title = book.get("title", "Unknown Book")
                rating = book.get("rating")
                
                author_name = ""
                contribs = book.get("contributions") or []
                if contribs:
                    author = contribs[0].get("author") or {}
                    author_name = author.get("name", "")
                
                rating_str = f" ({rating}⭐)" if rating is not None else ""
                
                if author_name:
                    line = f"• **{title}** by {author_name}{rating_str}\n"
                else:
                    line = f"• **{title}**{rating_str}\n"
                    
                books_text += line
                    
            embed.description = books_text
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching trending books:\n```\n{e}\n```")

    
    
async def setup(bot):
    await bot.add_cog(hardcoverCog(bot))
    print('hardcover cog loaded')
