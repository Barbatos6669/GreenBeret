import logging
from discord.ext import commands
import os
from dotenv import load_dotenv
import discord
import asyncio

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set up intents (including message content)
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.members = True
intents.guilds = True
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# List of cogs to load
COGS_TO_LOAD = [
    "cogs.tasks_generator",
    "cogs.delivery_manager",
    "cogs.delivery_point_display", 
    "cogs.opord_manager",
    "cogs.promotion",
    "cogs.player_stats",
    "cogs.medal_manager",

]

async def load_extensions():
    """
    Asynchronously load all extensions (cogs) for the bot.
    """
    for cog in COGS_TO_LOAD:
        try:
            await bot.load_extension(cog)
            logging.info(f"Loaded extension: {cog} successfully")
        except commands.ExtensionFailed as e:
            logging.error(f"Extension {cog} failed to load. Error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error loading extension {cog}. Error: {e}")

@bot.event
async def on_ready():
    """
    Event triggered when the bot is ready.
    """
    logging.info(f"Bot is ready! Logged in as {bot.user} ({bot.user.id})")

async def main():
    """
    Main entry point for the bot.
    """
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not DISCORD_BOT_TOKEN:
        logging.error("DISCORD_BOT_TOKEN is not set in environment variables.")
        return

    # Load extensions
    await load_extensions()

    # Start the bot
    try:
        await bot.start(DISCORD_BOT_TOKEN)
    except discord.LoginFailure as e:
        logging.error(f"Failed to log in: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred while starting the bot: {e}")

# Run the bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot shut down manually.")
    except Exception as e:
        logging.error(f"Critical error occurred: {e}")