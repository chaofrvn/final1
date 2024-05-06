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

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents)
tree = app_commands.CommandTree(client)
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    # if message.author == client.user:
    #     return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
@tree.command(
    name="price",
    description="Price of the stock ticker",
)
async def first_command(interaction):
    await interaction.response.send_message("Hello!")
@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

client.run(DISCORD_BOT_TOKEN)
