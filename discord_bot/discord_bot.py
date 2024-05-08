# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv,dotenv_values
import os
from influx_db import get_latest_price
from datetime import datetime
# load_dotenv(dotenv_path=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),".env"))
print(load_dotenv("../.env"))
DISCORD_BOT_TOKEN=os.environ["DISCORD_BOT_TOKEN"]
intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix='$', intents=intents)
tree = bot.tree
@bot.event
# async def on_message(message):
#     # if message.author == client.user:
#     #     return

#     if message.content.startswith('a'):
#         await message.channel.send('Hello!')
@bot.event
async def on_ready():
    await tree.sync()
    print(f'We have logged in as {bot.user}')
@tree.command(
    name="price",
    description="Price of the stock ticker",
)
@app_commands.describe(ticker="the ticker of the stock to show price")
async def first_command(interaction,ticker:str):
    obj=get_latest_price(ticker)
    time=obj[1].strftime('%Y-%m-%d %H:%M:%S')
    price=obj[0]
    await interaction.response.send_message(f'latest value of {ticker} is {price} at {time}')

bot.run(DISCORD_BOT_TOKEN)
