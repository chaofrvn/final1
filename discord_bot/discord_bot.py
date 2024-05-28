# This example requires the 'message_content' intent.
import discord
from discord.ext import commands, tasks
from discord import app_commands, File, Attachment
from dotenv import load_dotenv, dotenv_values
import os
from influx_db import (
    get_latest_data,
    get_latest_daily_data,
    get_all_time_data,
    get_single_day_data,
)
from mongo_db import addWarning
from chart import all_time_chart, one_day_chart
from datetime import datetime
import time
import asyncio
import functools
import typing
from confluent_kafka import Consumer, KafkaError
import concurrent.futures
import socket
import json

# load_dotenv(dotenv_path=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),".env"))
print(load_dotenv("../.env"))
consumer = Consumer(
    {
        "bootstrap.servers": "pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092",
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": "PLAIN",
        "sasl.username": "HGLHHLIGH5YQYKVX",
        "sasl.password": "gX5Smh7m7hoFTvIxUGPL9hwNJmgo1nQZBr/nHpFXD56jNm52m8i5C5Dor0/XMiD9",
        "group.id": "stock_warning",
        "auto.offset.reset": "latest",  # Start from the latest message
        "client.id": socket.gethostname(),
    }
)

# Subscribe to the Kafka topic
consumer.subscribe(["stockWarning"])
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
intents = discord.Intents.default()
intents.message_content = True


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        wrapped = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, wrapped)

    return wrapper


bot = commands.Bot(command_prefix="$", intents=intents)
tree = bot.tree


@bot.event
async def on_ready():
    await tree.sync()
    loop = asyncio.get_running_loop()
    print(f"We have logged in as {bot.user}")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Run the blocking function in an executor
        await loop.run_in_executor(executor, my_task, loop)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("a"):
        await message.channel.send("Hello!")


# Get the lastest price of 1 ticker (15m)
@tree.command(
    name="latest",
    description="Price of the stock ticker",
)
@app_commands.describe(
    ticker="the ticker to show price", type="the value to query(close, volume,...)"
)
async def latest(interaction, ticker: str, type: str = "close"):
    obj = await get_latest_data(ticker)
    await interaction.response.send_message(
        f'latest {type} value of {ticker} is {obj[type]} at {obj["_time"]}'
    )


# Get the latest daily price of 1 ticker ()
@tree.command(
    name="daily",
    description="Price of the stock ticker",
)
@app_commands.describe(
    ticker="the ticker to show price", type="the value to query(close, volume,...)"
)
async def daily(interaction, ticker: str, type: str = "close"):
    obj = await get_latest_daily_data(ticker)
    await interaction.response.send_message(
        f'latest daily {type} value of {ticker} is {obj[type]} at {obj["_time"]}'
    )


# Chart of daily_stock
@tree.command(
    name="daily_chart",
    description="Chart of the stock ticker",
)
@app_commands.describe(
    ticker="the ticker to show chart",
    field="the value to query(close, volume,...)",
    type="the indicator defalut is norma",
)
async def daily_chart(
    interaction: discord.Interaction,
    ticker: str,
    field: str = "close",
    type: str = "normal",
):
    data = await get_all_time_data(ticker=ticker, field=field, indicator=type)
    data_stream = await all_time_chart(ticker=ticker, field=type, data=data, title="")
    chart = discord.File(data_stream, filename="daily_chart.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://daily_chart.png")
    await interaction.response.send_message(embed=embed, file=chart)


# Chart of daily_stock
@tree.command(
    name="oneday_chart",
    description="Chart of one day stock ticker",
)
@app_commands.describe(
    ticker="the ticker to show chart",
    field="the value to query(close, volume,...)",
    type="the indicator default is normal",
    day="default day is current day",
)
async def oneday_chart(
    interaction: discord.Interaction,
    ticker: str,
    field: str = "close",
    day: str = datetime.now().date().strftime("%d-%m-%Y"),
):
    data = await get_single_day_data(ticker=ticker, day=day)
    data_stream = await one_day_chart(ticker=ticker, data=data, title="")
    chart = discord.File(data_stream, filename="oneday_chart.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://oneday_chart.png")
    await interaction.response.send_message(embed=embed, file=chart)


# Add alert into db
@tree.command(name="add_warning", description="Add warning for the stock")
@app_commands.describe(
    ticker="the ticker to add the waring",
    field="volume close high low",
    indicator="ma ema so",
    time_type="1D 15m",
    period="integer",
    compare="GREATER LESS",
    thresold="float",
)
async def add_waring(
    interaction: discord.Interaction,
    ticker: str,
    time_type: str,
    compare: str,
    thresold: str,
    period: int | None = None,
    field: str = None,
    indicator: str = None,
):
    thresold = float(thresold.replace(",", "."))
    user_id = interaction.user.id
    print(thresold)
    print(type(thresold))
    a = await addWarning(
        user_id=user_id,
        ticker=ticker,
        field=field,
        indicator=indicator,
        time_type=time_type,
        period=period,
        compare=compare,
        thresold=thresold,
    )
    await interaction.response.send_message(a)


def my_task(loop):
    print("my_task")
    try:
        while True:
            # print("my_task2")
            msg = consumer.poll(1)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Error while consuming: {msg.error()}")
            else:
                # Parse the received message
                # value = msg.value().decode('utf-8')
                # symbol, price = value.split(':')
                # push_data(json.load(msg.value()))\
                # print(type(msg.value()]))
                # push_data(type(msg.value().decode('utf-8')))
                # data=json.loads(msg.value().decode('utf-8'))
                user = asyncio.run_coroutine_threadsafe(
                    bot.fetch_user(int(msg.key())), loop
                ).result()
                asyncio.run_coroutine_threadsafe(
                    user.send(msg.value().decode("utf-8")), loop
                ).result()

    except KeyboardInterrupt:
        pass
    finally:
        # Close the consumer gracefully
        consumer.close()


bot.run(DISCORD_BOT_TOKEN)
