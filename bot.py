import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import setup_database


# ==================================================
# Configuration
# ==================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# PUT YOUR DISCORD SERVER ID HERE
GUILD_ID = 1545565762897444945


# ==================================================
# Intents
# ==================================================

intents = discord.Intents.default()

intents.members = True
intents.message_content = True


# ==================================================
# Bot
# ==================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==================================================
# Startup
# ==================================================

@bot.event
async def on_ready():

    print("--------------------------------")
    print(f"Logged in as: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("--------------------------------")

    guild = discord.Object(
        id=GUILD_ID
    )

    try:

        # Copy loaded commands to our test server
        bot.tree.copy_global_to(
            guild=guild
        )

        # Sync commands
        synced = await bot.tree.sync(
            guild=guild
        )

        print(
            f"Synced {len(synced)} command(s) "
            f"to your server."
        )

        for command in synced:

            print(
                f"  /{command.name}"
            )

    except Exception as error:

        print(
            f"Command sync failed: {error}"
        )


# ==================================================
# Main
# ==================================================

async def main():

    setup_database()

    async with bot:

        # Load our reaction-role system
        await bot.load_extension("cogs.reaction_roles")
        await bot.load_extension("cogs.autorole")
        # Start Discord connection
        await bot.start(TOKEN)


# ==================================================
# Start
# ==================================================

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN is missing from .env!"
    )


asyncio.run(main())
