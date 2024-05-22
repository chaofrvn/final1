# This example requires the 'message_content' intent.
import discord
from discord.ext import commands,tasks
from discord import app_commands,File
from dotenv import load_dotenv,dotenv_values
import os
from influx_db import get_latest_data,get_latest_daily_data,get_all_time_data
from mongo_db import addWarning
from chart import all_time_chart
from datetime import datetime
import time
import asyncio
import functools
import typing
# load_dotenv(dotenv_path=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),".env"))
print(load_dotenv("../.env"))
DISCORD_BOT_TOKEN=os.environ["DISCORD_BOT_TOKEN"]
intents = discord.Intents.default()
intents.message_content = True
def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        wrapped = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, wrapped)
    return wrapper

bot = commands.Bot(command_prefix='$', intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    print(f'We have logged in as {bot.user}')
        
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('a'):
        await message.channel.send('Hello!')
@tree.command(
    name="latest",
    description="Price of the stock ticker",
)
@app_commands.describe(ticker="the ticker to show price",type="the value to query(close, volume,...)")
async def latest(interaction,ticker:str,type:str="close"):
    obj=await get_latest_data(ticker)
    await interaction.response.send_message(f'latest {type} value of {ticker} is {obj[type]} at {obj["_time"]}')
@tree.command(
    name="daily",
    description="Price of the stock ticker",
)
@app_commands.describe(ticker="the ticker to show price",type="the value to query(close, volume,...)")
async def daily(interaction,ticker:str,type:str="close"):
    obj=await get_latest_daily_data(ticker)
    await interaction.response.send_message(f'latest daily {type} value of {ticker} is {obj[type]} at {obj["_time"]}')


@tree.command(
    name="daily_chart",
    description="Chart of the stock ticker",
)
@app_commands.describe(ticker="the ticker to show chart",field="the value to query(close, volume,...)",type="the indicator defalut is norma")
async def daily(interaction:discord.Interaction,ticker:str,field:str="close",type="normal"):
    data=await get_all_time_data(ticker=ticker,field=field,type=type)
    data_stream=await all_time_chart(ticker=ticker,field=type,data=data,title='')
    chart = discord.File(data_stream,filename="daily_chart.png")
    embed=discord.Embed()
    embed.set_image(
   url="attachment://daily_chart.png"
)
    await interaction.response.send_message(embed=embed, file=chart)



@tree.command(name="add_warning",description="Add warning for the stock")
@app_commands.describe(ticker="the ticker to add the waring",indicator="ma ema so",time_type="1D 15m",period="integer",compare="GREATER LESS",thresold="float")
async def add_waring(interaction:discord.Interaction,ticker:str,indicator:str,time_type:str,compare:str,thresold:float,period:int = 0):
    user_id=interaction.user.id
    a=await addWarning(user_id=user_id,ticker=ticker,indicator=indicator,time_type=time_type,period=period,compare=compare,thresold=thresold)
    await interaction.response.send_message(a)

bot.run(DISCORD_BOT_TOKEN)
