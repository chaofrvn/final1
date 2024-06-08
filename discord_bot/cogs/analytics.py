import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import discord
from discord.ext import commands
from discord import app_commands
from influx_db import (
    get_latest_data,
    get_latest_daily_data,
    get_all_time_data,
    get_single_day_data,
)
from chart import all_time_chart, one_day_chart
from datetime import datetime


class Analaytics(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree

    @commands.Cog.listener()
    async def on_ready(self):
        print("Analaytics cog loaded")

    @app_commands.command(
        name="latest",
        description="Price of the stock ticker",
    )
    @app_commands.describe(
        ticker="the ticker to show price", type="the value to query(close, volume,...)"
    )
    async def latest(
        self, interaction: discord.Interaction, ticker: str, type: str = "close"
    ):
        obj = await get_latest_data(ticker)
        await interaction.response.send_message(
            f'latest {type} value of {ticker} is {obj[type]} at {obj["_time"]}'
        )

    # Get the latest daily price of 1 ticker (1D)
    @app_commands.command(
        name="daily",
        description="Price of the stock ticker",
    )
    @app_commands.describe(
        ticker="the ticker to show price", type="the value to query(close, volume,...)"
    )
    async def daily(
        self, interaction: discord.Interaction, ticker: str, type: str = "close"
    ):
        obj = await get_latest_daily_data(ticker)
        await interaction.response.send_message(
            f'latest daily {type} value of {ticker} is {obj[type]} at {obj["_time"]}'
        )

    # Chart of daily_stock
    @app_commands.command(
        name="daily_chart",
        description="Chart of the stock ticker",
    )
    @app_commands.describe(
        ticker="the ticker to show chart",
        field="the value to query(close, volume,...)",
        indicator="the indicator ",
    )
    async def daily_chart(
        self,
        interaction: discord.Interaction,
        ticker: str,
        field: str = None,
        indicator: str = None,
        period: int = None,
    ):
        data = await get_all_time_data(
            ticker=ticker, field=field, indicator=indicator, period=period
        )

        data_stream = all_time_chart(
            ticker=ticker,
            field=field,
            indicator=indicator,
            data=data,
        )

        chart = discord.File(data_stream, filename="daily_chart.png")
        embed = discord.Embed(title="Đây là biểu đồ của bạn:")
        embed.set_image(url="attachment://daily_chart.png")
        await interaction.response.send_message(embed=embed, file=chart)

    # Chart of oneday_stock
    @app_commands.command(
        name="oneday_chart",
        description="Chart of one day stock ticker",
    )
    @app_commands.describe(
        ticker="the ticker to show chart",
        field="the value to query(close, volume,...)",
        indicator="chỉ báo",
        day="default day is current day",
    )
    async def oneday_chart(
        self,
        interaction: discord.Interaction,
        ticker: str,
        field: str = None,
        indicator: str = None,
        period: int = None,
        day: str = datetime.now().date().strftime("%d-%m-%Y"),
    ):
        data = await get_single_day_data(
            ticker=ticker, indicator=indicator, field=field, day=day, period=period
        )
        data_stream = one_day_chart(
            ticker=ticker, data=data, indicator=indicator, field=field
        )
        chart = discord.File(data_stream, filename="oneday_chart.png")
        embed = discord.Embed(title="Đây là biểu đồ của bạn:")
        embed.set_image(url="attachment://oneday_chart.png")
        await interaction.response.send_message(embed=embed, file=chart)


async def setup(client):
    await client.add_cog(Analaytics(bot=client))
