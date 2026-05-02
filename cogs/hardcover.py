import discord
from discord import app_commands
from discord.ext import commands
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio
import os
import json
from datetime import datetime, timedelta

def load_book_choices():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    choices_file = os.path.join(base_dir, 'configs', 'book_choices.json')
    if os.path.exists(choices_file):
        try:
            with open(choices_file, 'r', encoding='utf-8') as f:
                books = json.load(f)
                return [app_commands.Choice(name=book, value=book) for book in books][:25]
        except Exception as e:
            print(f"Error loading book choices: {e}")
    return [app_commands.Choice(name="The Poppy War", value="The Poppy War")]

BOOK_CHOICES = load_book_choices()

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

    @app_commands.command(name="ratings", description="Show user ratings for a specific book")
    @app_commands.describe(book_title="Select a book from the list")
    @app_commands.choices(book_title=BOOK_CHOICES)
    async def ratings(self, interaction: discord.Interaction, book_title: app_commands.Choice[str]):
        await interaction.response.defer()
        
        search_title = book_title.value
        
        # Load registered users
        user_file = 'db/hardcover_users.json'
        users = {}
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    users = json.load(f)
            except json.JSONDecodeError:
                pass
        
        if not users:
            await interaction.followup.send("No registered Hardcover users found.")
            return
        
        # Search for the selected book
        search_query = """
        query SearchBook($title: String!) {
            books(where: {title: {_eq: $title}}, limit: 1, order_by: {users_count: desc_nulls_last}) {
                id
                title
                image {
                    url
                }
                contributions(limit: 1) {
                    author {
                        name
                    }
                }
            }
        }
        """
        
        try:
            async with self.client as session:
                query = gql(search_query)
                search_result = await session.execute(query, variable_values={"title": search_title})
                
                books_data = search_result.get("books", [])
                
                if not books_data:
                    # Fallback to Title Cased match
                    search_result = await session.execute(query, variable_values={"title": search_title.title()})
                    books_data = search_result.get("books", [])
                    
                if not books_data:
                    await interaction.followup.send(f"Could not find '{search_title}' on Hardcover. Note: Due to recent API limits, an exact title match is required (e.g., 'The Poppy War').")
                    return
                
                book = books_data[0]
                book_id = book.get("id")
                title = book.get("title")
                image_data = book.get("image") or {}
                image_url = image_data.get("url")
                
                author_name = ""
                contribs = book.get("contributions") or []
                if contribs:
                    author = contribs[0].get("author") or {}
                    author_name = author.get("name", "")
                
                # Get ratings from all registered users for this book
                ratings_data = []

                user_ids = []
                usernames = []
                for identifier in users.values():
                    if identifier.isdigit():
                        user_ids.append(int(identifier))
                    else:
                        usernames.append(identifier)
                        
                ratings_query = """
                query GetUsersRatings($book_id: Int!, $usernames: [citext!], $user_ids: [Int!]) {
                    users(where: {
                        _or: [
                            {username: {_in: $usernames}},
                            {id: {_in: $user_ids}}
                        ]
                    }) {
                        id
                        username
                        name
                        user_books(where: {book_id: {_eq: $book_id}}, limit: 1) {
                            rating
                        }
                    }
                }
                """
                params = {
                    "book_id": book_id,
                    "usernames": usernames,
                    "user_ids": user_ids
                }
                
                try:
                    r_query = gql(ratings_query)
                    result = await session.execute(r_query, variable_values=params)
                    
                    users_data = result.get("users", [])
                    api_users = {}
                    for u in users_data:
                        if u.get("username"):
                            api_users[u.get("username").lower()] = u
                        if u.get("id"):
                            api_users[str(u.get("id"))] = u
                            
                    for identifier in set(users.values()):
                        user = api_users.get(identifier.lower())
                        if user:
                            display_name = user.get("username") or user.get("name") or identifier
                            user_books = user.get("user_books", [])
                            if user_books:
                                rating = user_books[0].get("rating")
                            else:
                                rating = None
                        else:
                            display_name = identifier
                            rating = None
                            
                        ratings_data.append({
                            "name": display_name,
                            "rating": rating
                        })
                except Exception as e:
                    print(f"Error fetching ratings: {e}")
                
                if not ratings_data:
                    await interaction.followup.send(f"No registered users have rated '{title}' yet.")
                    return
            
            # Sort by rating (highest first)
            ratings_data.sort(key=lambda x: x["rating"] if x["rating"] is not None else -1, reverse=True)
            
            embed = discord.Embed(
                title=f"Ratings for {title}",
                color=discord.Color.blue()
            )
            
            if image_url:
                embed.set_thumbnail(url=image_url)
                
            if author_name:
                embed.add_field(name="Author", value=author_name, inline=False)
            
            ratings_text = ""
            for data in ratings_data:
                if data["rating"] is not None:
                    ratings_text += f"**{data['name']}**: {data['rating']} ⭐\n"
                else:
                    ratings_text += f"**{data['name']}**: No rating\n"
            
            embed.description = ratings_text
            embed.set_footer(text="Powered by Hardcover API")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching ratings:\n```\n{e}\n```")

    @app_commands.command(name="readingprogress", description="Show user reading progress for a specific book")
    @app_commands.describe(book_title="Select a book from the list")
    @app_commands.choices(book_title=BOOK_CHOICES)
    async def readingprogress(self, interaction: discord.Interaction, book_title: app_commands.Choice[str]):
        await interaction.response.defer()
        
        search_title = book_title.value
        
        # Load registered users
        user_file = 'db/hardcover_users.json'
        users = {}
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    users = json.load(f)
            except json.JSONDecodeError:
                pass
        
        if not users:
            await interaction.followup.send("No registered Hardcover users found.")
            return
        
        # Search for the selected book
        search_query = """
        query SearchBook($title: String!) {
            books(where: {title: {_eq: $title}}, limit: 1, order_by: {users_count: desc_nulls_last}) {
                id
                title
                image {
                    url
                }
                contributions(limit: 1) {
                    author {
                        name
                    }
                }
            }
        }
        """
        
        try:
            async with self.client as session:
                query = gql(search_query)
                search_result = await session.execute(query, variable_values={"title": search_title})
                
                books_data = search_result.get("books", [])
                
                if not books_data:
                    # Fallback to Title Cased match
                    search_result = await session.execute(query, variable_values={"title": search_title.title()})
                    books_data = search_result.get("books", [])
                    
                if not books_data:
                    await interaction.followup.send(f"Could not find '{search_title}' on Hardcover. Note: Due to recent API limits, an exact title match is required (e.g., 'The Poppy War').")
                    return
                
                book = books_data[0]
                book_id = book.get("id")
                title = book.get("title")
                image_data = book.get("image") or {}
                image_url = image_data.get("url")
                
                author_name = ""
                contribs = book.get("contributions") or []
                if contribs:
                    author = contribs[0].get("author") or {}
                    author_name = author.get("name", "")
                
                # Get progress from all registered users for this book
                progress_data = []

                user_ids = []
                usernames = []
                for identifier in users.values():
                    if identifier.isdigit():
                        user_ids.append(int(identifier))
                    else:
                        usernames.append(identifier)
                        
                progress_query = """
                query GetUsersProgress($book_id: Int!, $usernames: [citext!], $user_ids: [Int!]) {
                    users(where: {
                        _or: [
                            {username: {_in: $usernames}},
                            {id: {_in: $user_ids}}
                        ]
                    }) {
                        id
                        username
                        name
                        user_books(where: {book_id: {_eq: $book_id}}, limit: 1) {
                            status_id
                            user_book_reads(limit: 1, order_by: {started_at: desc_nulls_last}) {
                                progress
                            }
                        }
                    }
                }
                """
                params = {
                    "book_id": book_id,
                    "usernames": usernames,
                    "user_ids": user_ids
                }
                
                try:
                    p_query = gql(progress_query)
                    result = await session.execute(p_query, variable_values=params)
                    
                    users_data = result.get("users", [])
                    api_users = {}
                    for u in users_data:
                        if u.get("username"):
                            api_users[u.get("username").lower()] = u
                        if u.get("id"):
                            api_users[str(u.get("id"))] = u
                            
                    for identifier in set(users.values()):
                        user = api_users.get(identifier.lower())
                        if user:
                            display_name = user.get("username") or user.get("name") or identifier
                            user_books = user.get("user_books", [])
                            if user_books:
                                ub = user_books[0]
                                status_id = ub.get("status_id")
                                reads = ub.get("user_book_reads", [])
                                progress = reads[0].get("progress") if reads else None
                            else:
                                status_id = 0
                                progress = None
                        else:
                            display_name = identifier
                            status_id = 0
                            progress = None
                            
                        progress_data.append({
                            "name": display_name,
                            "status_id": status_id,
                            "progress": progress
                        })
                except Exception as e:
                    print(f"Error fetching progress: {e}")
                
                if not progress_data:
                    await interaction.followup.send(f"No registered users have '{title}' tracked yet.")
                    return
            
            # Sort by status (finished first), then progress (highest first)
            progress_data.sort(key=lambda x: (
                x["status_id"] if x["status_id"] is not None else -1,
                x["progress"] if x["progress"] is not None else -1
            ), reverse=True)
            
            embed = discord.Embed(
                title=f"Reading Progress for {title}",
                color=discord.Color.green()
            )
            
            if image_url:
                embed.set_thumbnail(url=image_url)
                
            if author_name:
                embed.add_field(name="Author", value=author_name, inline=False)
            
            progress_text = ""
            for data in progress_data:
                status_id = data["status_id"]
                progress = data["progress"]
                name = data["name"]
                
                if status_id == 3:
                    progress_text += f"**{name}**: Finished 🏁\n"
                elif status_id == 2:
                    if progress is not None:
                        progress_text += f"**{name}**: Currently Reading ({progress}%)\n"
                    else:
                        progress_text += f"**{name}**: Currently Reading\n"
                elif status_id == 1:
                    progress_text += f"**{name}**: Want to Read\n"
                elif status_id == 0:
                    progress_text += f"**{name}**: Not Reading\n"
                else:
                    if progress is not None:
                        progress_text += f"**{name}**: {progress}%\n"
                    else:
                        progress_text += f"**{name}**: Tracked (Unknown status)\n"
                        
            embed.description = progress_text
            embed.set_footer(text="Powered by Hardcover API")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching progress:\n```\n{e}\n```")

    
    
async def setup(bot):
    await bot.add_cog(hardcoverCog(bot))
    print('hardcover cog loaded')
