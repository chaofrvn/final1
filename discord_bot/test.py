import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv, dotenv_values
import os

# from influx_db import get_latest_price
from datetime import datetime
import time
import asyncio

# load_dotenv(dotenv_path=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),".env"))
print(load_dotenv("../.env"))
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix="$", intents=intents)
tree = bot.tree


@bot.event
async def on_ready():
    print("Success: Bot is connected to Discord")
    await bot.tree.sync()


@bot.event
async def on_message(message):
    # if message.author == client.user:
    #     return

    if message.content.startswith("a"):
        await message.channel.send("Hello!")


@bot.command(name="sync")
async def sync(ctx):
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s).")
    print(synced)


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith("py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    async with bot:
        await load()
        await bot.start(DISCORD_BOT_TOKEN)


asyncio.run(main())

# bot.run(DISCORD_BOT_TOKEN)
