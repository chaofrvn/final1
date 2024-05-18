import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv,dotenv_values
import os
from influx_db import get_latest_price
from datetime import datetime
import time
import asyncio
# load_dotenv(dotenv_path=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),".env"))
print(load_dotenv("../.env"))
DISCORD_BOT_TOKEN=os.environ["DISCORD_BOT_TOKEN"]
intents = discord.Intents.default()
intents.message_content = True
async def my_task():
    # Blocking operation using time.sleep()
    time.sleep(100)
    print("Task completed")

bot = commands.Bot(command_prefix='$', intents=intents)
tree = bot.tree
@bot.event
async def on_message(message):
    # if message.author == client.user:
    #     return

    if message.content.startswith('a'):
        await message.channel.send('Hello!')


bot.run(DISCORD_BOT_TOKEN)