import os
import sys
import inspect
from pydantic import (
    BaseModel,
    field_validator,
    ValidationError,
    model_validator,
    Field,
    conint,
    PositiveInt,
)
from typing import List, ClassVar, Optional
import pandas as pd

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

df = pd.read_csv("../test_producer/company.csv")
tickers_list = df["ticker"].tolist()


class CommandInput(BaseModel):
    ticker: str
    field: Optional[str]
    indicator: Optional[str]
    period: Optional[int]

    _allowed_tickers: ClassVar[List[str]] = tickers_list  # List of valid tickers
    _allowed_fields: ClassVar[List[str]] = [
        "close",
        "volume",
        "high",
        "low",
        "open",
    ]  # List of valid fields
    _allowed_indicators: ClassVar[List[str]] = ["ma", "ema", "stoch", "rsi"]

    # @field_validator("ticker")
    # def validate_ticker(cls, value):

    #     if value not in cls._allowed_tickers:

    #         raise ValueError(f"Ticker must be one of ")

    #     print(3)
    #     return value

    # @field_validator("field")
    # def validate_field(cls, value):
    #     if value not in cls._allowed_fields:
    #         raise ValueError(f"field must be one of {cls._allowed_fields}")

    #     return value

    @model_validator(mode="before")
    def check(cls, values):
        ticker = values.get("ticker")
        field = values.get("field")
        indicator = values.get("indicator")
        period = values.get("period")

        # ticker phải thuộc danh sách cho trước
        if ticker not in cls._allowed_tickers:
            raise ValueError(f"Ticker {ticker} is not allowed.")

        # indicator phải thuộc danh sách cho trước
        if indicator and indicator not in cls._allowed_indicators:
            raise ValueError(f"Indicator {indicator} is not allowed.")

        # field phải thuộc danh sách cho trước
        if field and field not in cls._allowed_fields:
            raise ValueError(f"Field {field} is not allowed.")

        # Nếu indicator là stoch hoặc rsi thì không được nhập field
        if indicator in {"stoch", "rsi"} and field:
            raise ValueError(f"If indicator is {indicator}, field must be None.")

        # Nếu indicator là ma hoặc ema thì bắt buộc nhập field
        if indicator in {"ma", "ema"} and not field:
            raise ValueError(f"If indicator is {indicator}, field is required.")

        # Nếu không có indicator thì không có period
        if not indicator and period:
            raise ValueError("Không cần nhập giá trị period")

        # Có thể không nhập indicator, khi đó bắt buộc nhập field
        if not indicator and not field:
            raise ValueError("If indicator is None, field is required.")

        return values


class DataModel1(BaseModel):
    ticker: str
    field: Optional[str]
    indicator: Optional[str]
    period: Optional[PositiveInt]  # period phải là số nguyên dương

    _allowed_tickers: ClassVar[List[str]] = tickers_list
    _allowed_fields: ClassVar[List[str]] = [
        "close",
        "volume",
        "high",
        "low",
        "open",
    ]
    _allowed_indicators: ClassVar[List[str]] = ["ma", "ema", "stoch", "rsi"]

    @model_validator(mode="before")
    def check_constraints(cls, values):
        print(values)
        ticker = values.get("ticker")
        field = values.get("field")
        indicator = values.get("indicator")
        period = values.get("period")
        print(ticker + "----------------------")

        # ticker phải thuộc danh sách cho trước
        if ticker not in cls._allowed_tickers:
            raise ValueError(f"Ticker {ticker} is not allowed.")

        # indicator phải thuộc danh sách cho trước
        if indicator and indicator not in cls._allowed_indicators:
            raise ValueError(f"Indicator {indicator} is not allowed.")

        # field phải thuộc danh sách cho trước
        if field and field not in cls._allowed_fields:
            raise ValueError(f"Field {field} is not allowed.")

        # Nếu indicator là stoch hoặc rsi thì không được nhập field
        if indicator in {"stoch", "rsi"} and field:
            raise ValueError(f"If indicator is {indicator}, field must be None.")

        # Nếu indicator là ma hoặc ema thì bắt buộc nhập field
        if indicator in {"ma", "ema"} and not field:
            raise ValueError(f"If indicator is {indicator}, field is required.")

        # Nếu không có indicator thì không có period
        if not indicator and period:
            raise ValueError("Không cần nhập giá trị period")

        # Có thể không nhập indicator, khi đó bắt buộc nhập field
        if not indicator and not field:
            raise ValueError("If indicator is None, field is required.")

        return values


class DataModel2(BaseModel):
    ticker: str
    field: Optional[str]
    indicator: Optional[str]
    period: Optional[PositiveInt]  # period phải là số nguyên dương
    day: str

    _allowed_tickers: ClassVar[List[str]] = tickers_list
    _allowed_fields: ClassVar[List[str]] = [
        "close",
        "volume",
        "high",
        "low",
        "open",
    ]
    _allowed_indicators: ClassVar[List[str]] = ["ma", "ema", "stoch", "rsi"]

    @model_validator(mode="before")
    def check_constraints(cls, values):
        print(values)
        ticker = values.get("ticker")
        field = values.get("field")
        indicator = values.get("indicator")
        period = values.get("period")
        day = values.get("day")
        print(ticker + "----------------------")

        # ticker phải thuộc danh sách cho trước
        if ticker not in cls._allowed_tickers:
            raise ValueError(f"Ticker {ticker} is not allowed.")

        # indicator phải thuộc danh sách cho trước
        if indicator and indicator not in cls._allowed_indicators:
            raise ValueError(f"Indicator {indicator} is not allowed.")

        # field phải thuộc danh sách cho trước
        if field and field not in cls._allowed_fields:
            raise ValueError(f"Field {field} is not allowed.")

        # Nếu indicator là stoch hoặc rsi thì không được nhập field
        if indicator in {"stoch", "rsi"} and field:
            raise ValueError(f"If indicator is {indicator}, field must be None.")

        # Nếu indicator là ma hoặc ema thì bắt buộc nhập field
        if indicator in {"ma", "ema"} and not field:
            raise ValueError(f"If indicator is {indicator}, field is required.")

        # Nếu không có indicator thì không có period
        if not indicator and period:
            raise ValueError("Không cần nhập giá trị period")

        # Có thể không nhập indicator, khi đó bắt buộc nhập field
        if not indicator and not field:
            raise ValueError("If indicator is None, field is required.")

        try:
            day_date = datetime.strptime(day, "%d-%m-%Y")
        except Exception as e:
            print(e)
            raise ValueError("day must be in the format 'dd-mm-yyyy'")

        # Kiểm tra ngày phải là ngày hôm nay hoặc trước đó
        if day_date > datetime.now():
            raise ValueError("day must be today or in the past")

        return values


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
        ticker="the ticker to show price",
        field="the value to query(close, volume,...)",
        indicator="the indicator (ma, ema, ...)",
        period="the period of indicator",
    )
    async def latest(
        self,
        interaction: discord.Interaction,
        ticker: str,
        field: str = None,
        indicator: str = None,
        period: int = None,
    ):
        try:
            validated_data = CommandInput(
                ticker=ticker, field=field, indicator=indicator, period=period
            )
        except ValidationError as e:
            await interaction.response.send_message(
                f"Error: {e.errors()[0]['msg']}", ephemeral=True
            )
            return

        return await interaction.response.send_message("success")
        # obj = await get_latest_data(ticker)
        # await interaction.response.send_message(
        #     f'latest {field} value of {ticker} is {obj[field]} at {obj["_time"]}'
        # )

    # Get the latest daily price of 1 ticker (1D)
    @app_commands.command(
        name="daily",
        description="Price of the stock ticker",
    )
    @app_commands.describe(
        ticker="the ticker to show price", field="the value to query(close, volume,...)"
    )
    async def daily(
        self,
        interaction: discord.Interaction,
        ticker: str,
        field: str = None,
        indicator: str = None,
        period: int = None,
    ):
        try:
            validated_data = CommandInput(
                ticker=ticker, field=field, indicator=indicator, period=period
            )
        except ValidationError as e:
            await interaction.response.send_message(
                f"Error: {e.errors()[0]['msg']}", ephemeral=True
            )
            return
        # obj = await get_latest_daily_data(ticker)
        # await interaction.response.send_message(
        #     f'latest daily {field} value of {ticker} is {obj[field]} at {obj["_time"]}'
        # )

    # Chart of daily_stock
    @app_commands.command(
        name="daily_chart",
        description="Chart of the stock ticker",
    )
    @app_commands.describe(
        ticker="the ticker to show chart",
        field="the value to query(close, volume,...)",
        indicator="the indicator ",
        period="độ dài khoảng thời gian để vẽ biểu đồ",
    )
    async def daily_chart(
        self,
        interaction: discord.Interaction,
        ticker: str,
        field: str = None,
        indicator: str = None,
        period: int = None,
    ):
        try:
            validated_data = DataModel1(
                ticker=ticker, field=field, indicator=indicator, period=period
            )
        except ValidationError as e:
            await interaction.response.send_message(
                f"Error: {e.errors()[0]['msg']}", ephemeral=True
            )
            return
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
        try:
            validated_data = DataModel2(
                ticker=ticker, field=field, indicator=indicator, period=period, day=day
            )
        except ValidationError as e:
            await interaction.response.send_message(
                f"Error: {e.errors()[0]['msg']}", ephemeral=True
            )
            return
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
