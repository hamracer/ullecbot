import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium_stealth import stealth
import time
import random
import io

# A list of channel IDs where the command is allowed
ALLOWED_CHANNEL_IDS = [562352225423458326,1390614043546353694,262371002577715201]

class clubCog(commands.Cog, name="club"):
    def __init__(self, bot):
        self.bot = bot

    def get_club_screenshot(self, circle_id: str):
        # --- Setup Selenium Options ---
        options = Options()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--headless")
        options.add_argument("--window-size=3440,1600")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        driver = None
        try:
            # --- Initialize Driver ---
            driver = webdriver.Chrome(options=options)

            # --- Apply Stealth ---
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
            )

            base_url = "https://chronogenesis.net"
            page_url = f"{base_url}/club_profile?circle_id={circle_id}"
            print(f"\nAttempting to access page for circle ID: {circle_id}")
            
            driver.get(page_url)
            wait = WebDriverWait(driver, 60)

            print("Waiting for page to load...")
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading-div")))
            print("Page has loaded.")

            time.sleep(random.uniform(1, 2))

            # --- Click the "Show Data" button ---
            print("Waiting for the 'Show Data' button...")
            show_data_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "expand-button")))
            show_data_button.click()
            print("Button clicked.")

            time.sleep(5)

            # --- Take a screenshot of the relevant element ---
            print("Finding profile element 'common-root'...")
            profile_element = driver.find_element(By.CLASS_NAME, "common-root")
            
            print("Resizing element to ensure full table is visible...")
            driver.execute_script(
                "arguments[0].style.height = 'auto'; arguments[0].style.maxHeight = 'none'; arguments[0].style.overflow = 'visible';",
                profile_element
            )
            time.sleep(1)

            print("Taking screenshot...")
            screenshot_bytes = profile_element.screenshot_as_png
            
            print("\n✅ Success! Screenshot captured in memory.")
            return screenshot_bytes

        except TimeoutException:
            print(f"Error: A timeout occurred while loading the page for club ID {circle_id}.")
            return None
        except NoSuchElementException:
            print(f"Error: Could not find a necessary element on the page for club ID {circle_id}. The ID might be invalid.")
            return None
        except Exception as e:
            print(f"\n--- An unexpected error occurred ---")
            print(e)
            return None
        finally:
            if driver:
                print("\nScript finished. Closing browser.")
                driver.quit()

    @commands.command()
    @commands.is_owner()
    async def club(self, ctx, *, circle_id: str = None):
        """Fetches a club profile, screenshots it, and sends the image."""
        if ctx.channel.id not in ALLOWED_CHANNEL_IDS:
            return

        if not circle_id:
            await ctx.reply("BAKKAAAA Usage: `!club <ID>`")
            return

        processing_message = await ctx.reply(f"🔍 Fetching data for club `{circle_id}`... this might take a moment.")
        
        screenshot_bytes = await self.bot.loop.run_in_executor(
            None, self.get_club_screenshot, circle_id
        )

        await processing_message.delete()
        
        if screenshot_bytes:
            with io.BytesIO(screenshot_bytes) as image_file:
                await ctx.reply(file=discord.File(image_file, f"club_{circle_id}.png"))
        else:
            await ctx.reply(f"Something went wrong!!!")

async def setup(bot):
    await bot.add_cog(clubCog(bot))
    print('club cog loaded')