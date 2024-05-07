# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv,dotenv_values
import os
# load_dotenv(dotenv_path=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),".env"))
print(load_dotenv("../.env"))
DISCORD_BOT_TOKEN=os.environ["DISCORD_BOT_TOKEN"]
intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix='$', intents=intents)
tree = bot.tree
@bot.event
async def on_message(message):
    # if message.author == client.user:
    #     return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
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
    await interaction.response.send_message("Hello! "+ticker)
bot.run(DISCORD_BOT_TOKEN)
