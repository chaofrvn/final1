import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import app_commands, File, Attachment, errors
from discord.app_commands import Choice
from dotenv import load_dotenv, dotenv_values
from typing import Literal, ClassVar, Optional, List
import os
from View.edit_warning import comfirmEditWarning
from View.delete_warning import comfirmDeleteWarning
from pydantic import (
    BaseModel,
    field_validator,
    ValidationError,
    model_validator,
    Field,
    conint,
    PositiveInt,
)

from mongo_db import addWarning, getWarning, getWarningByObjectID
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
import pandas as pd

print(load_dotenv("../.env"))


df = pd.read_csv("../stock_data_producer/company.csv")
tickers_list = df["ticker"].tolist()


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        wrapped = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, wrapped)

    return wrapper


class DataModel3(BaseModel):
    ticker: str
    field: Optional[str]
    indicator: Optional[str]
    threshold: str
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
        threshold = values.get("threshold")
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

        # Nếu không có indicator thì không có period và ngược lại
        if (indicator is None and period is not None) or (
            indicator is not None and period is None
        ):
            raise ValueError(
                "Both indicator and period must be provided together or neither"
            )

        # Có thể không nhập indicator, khi đó bắt buộc nhập field
        if not indicator and not field:
            raise ValueError("If indicator is None, field is required.")

        # Xac thuc threshold
        if not threshold.replace(".", "", 1).replace(",", "", 1).isdigit():
            raise ValueError(
                "threshold must only contain digits and at most one . or ,"
            )

        return values


class Warning(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        "Command on Cooldown"
        if isinstance(err, errors.CommandOnCooldown):
            await ctx.send(
                f":stopwatch: Command is on Cooldown for **{err.retry_after:.2f}** seconds."
            )
            " Missing Permissions "
        elif isinstance(err, errors.MissingPermissions):
            await ctx.send(f":x: You can't use that command.")
            " Missing Arguments "
        elif isinstance(err, commands.MissingRequiredArgument):
            await ctx.send(f":x: Required arguments aren't passed.")
            " Command not found "
        elif isinstance(err, errors.CommandNotFound):
            pass
            " Any Other Error "
        else:
            ss = get(self.bot.guilds, id=791553406266245121)
            report = get(ss.text_channels, id=791556612715708448)
            embed = discord.Embed(
                title="An Error has occurred",
                description=f"Error: \n `{err}`",
                timestamp=ctx.message.created_at,
                color=242424,
            )
            await report.send(embed=embed)
            print(err)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Warning cog loaded")

    # Add alert into db
    @app_commands.command(
        name="thêm_cảnh_báo", description="Thêm các cảnh báo cho người dùng"
    )
    @app_commands.choices(
        time_type=[Choice(name="1 ngày", value=0), Choice(name="15 phút", value=1)],
        compare=[Choice(name="Lớn hơn", value=1), Choice(name="Bé hơn", value=0)],
    )
    @app_commands.describe(
        ticker="the ticker to add the waring",
        field="volume close high low",
        indicator="ma ema so",
        time_type="1D 15m",
        period="integer",
        compare="GREATER LESS",
        threshold="float",
    )
    @app_commands.rename(
        ticker="mã_cổ_phiếu",
        field="trường",
        indicator="chỉ_báo",
        time_type="loại_thời_gian",
        period="chu_kì",
        compare="so_sánh",
        threshold="ngưỡng",
    )
    async def add_warning(
        self,
        interaction: discord.Interaction,
        ticker: str,
        time_type: Choice[int],
        compare: Choice[int],
        threshold: str,
        period: int | None = None,
        field: str = None,
        indicator: str = None,
    ):

        try:
            validated_data = DataModel3(
                ticker=ticker,
                field=field,
                indicator=indicator,
                period=period,
                threshold=threshold,
            )
        except ValidationError as e:
            await interaction.response.send_message(
                f"Error: {e.errors()[0]['msg']}", ephemeral=True
            )
            return

        threshold = float(threshold.replace(",", "."))
        user_id = interaction.user.id
        time_type = bool(time_type.value)
        compare = bool(compare.value)
        try:
            print(1)
            await addWarning(
                user_id=user_id,
                ticker=ticker,
                field=field,
                indicator=indicator,
                time_type=time_type,
                period=period,
                compare=compare,
                thresold=threshold,
            )
            print(2)
        except Exception as e:
            print(e)
        await interaction.response.send_message("Bạn đã thêm cảnh báo thành công")
        # await interaction.response.send_modal(addWarningModal())

    @app_commands.command(
        name="đọc_cảnh_báo", description="Đọc các cảnh báo mà bạn đã tạo ra"
    )
    @app_commands.describe()
    async def getAllWarning(self, interaction: discord.Interaction):
        print("testhihi")
        user_id = interaction.user.id
        warnings = await getWarning(user_id)
        if len(warnings) == 0:
            return await interaction.response.send_message(
                "Bạn chưa có cảnh báo để xem"
            )
        warnings = warnings[0]["warnings"]
        embed = discord.Embed(title="**Danh sách các mã cổ phiếu**")
        nl = "\n"
        for index, warning in enumerate(warnings):
            embed.add_field(
                name=f'**{index+1}.Mã cảnh báo: {warning["_id"]}**',
                value=f"""
    > Mã cổ phiếu: {warning["ticker"]}
    > Loại thời gian :{"15 phút" if warning["is_15_minute"] else "1 ngày"}
    {"" if (warning["field"] is None) else f'> Trường: {warning["field"]}'+nl}{"" if (warning["indicator"] is None) else f'> Chỉ báo: {warning["indicator"]}'+nl}{"" if (warning["period"] is None) else f'> Chu kì: {warning["period"]}'+nl}> So sánh:{"Lớn hơn" if warning["is_greater"] else "Bé hơn"}
    > Ngưỡng:{warning["thresold"]}
    """,
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="xóa_cảnh_báo", description="Xóa một cảnh báo")
    @app_commands.describe(id="Mã cảnh báo bạn muốn xóa")
    @app_commands.rename(id="mã_cảnh_báo")
    async def delete_warning(self, interaction: discord.Interaction, id: str):
        warning = await getWarningByObjectID(interaction.user.id, id)
        if warning is None:
            await interaction.response.send_message(
                "Bạn không có mã cảnh báo với ID này"
            )
        else:
            await interaction.response.defer()
            nl = "\n"
            embed = discord.Embed(title="**Mã cổ phiếu cần xóa**")
            embed.add_field(
                name=f'**Mã cảnh báo: {warning["_id"]}**',
                value=f"""
    > Mã cổ phiếu: {warning["ticker"]}
    > Loại thời gian :{"15 phút" if warning["is_15_minute"] else "1 ngày"}
    {"" if (warning["field"] is None) else f'> Trường: {warning["field"]}'+nl}{"" if (warning["indicator"] is None) else f'> Chỉ báo: {warning["indicator"]}'+nl}{"" if (warning["period"] is None) else f'> Chu kì: {warning["period"]}'+nl}> So sánh:{"Lớn hơn" if warning["is_greater"] else "Bé hơn"}
    > Ngưỡng:{warning["thresold"]}
    """,
                inline=False,
            )
            view = comfirmDeleteWarning(warning_id=warning["_id"], timeout=60)
            await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="sửa_cảnh_báo", description="Sửa một cảnh báo")
    @app_commands.choices(
        time_type=[Choice(name="1 ngày", value=0), Choice(name="15 phút", value=1)],
        compare=[Choice(name="Lớn hơn", value=1), Choice(name="Bé hơn", value=0)],
    )
    @app_commands.describe(
        id="Mã cảnh báo bạn muốn sửa",
        ticker="the ticker to add the waring",
        field="volume close high low",
        indicator="ma ema so",
        time_type="1D 15m",
        period="integer",
        compare="GREATER LESS",
        threshold="float",
    )
    @app_commands.rename(
        id="mã_cảnh_báo",
        ticker="mã_cổ_phiếu",
        field="trường",
        indicator="chỉ_báo",
        time_type="loại_thời_gian",
        period="chu_kì",
        compare="so_sánh",
        threshold="ngưỡng",
    )
    async def edit_warning(
        self,
        interaction: discord.Interaction,
        id: str,
        ticker: str = None,
        time_type: Choice[int] = None,
        compare: Choice[int] = None,
        threshold: str = None,
        period: int = None,
        field: str = None,
        indicator: str = None,
    ):
        old_warning = await getWarningByObjectID(interaction.user.id, id)
        if old_warning is None:
            await interaction.response.send_message(
                "Bạn không có mã cảnh báo với ID này"
            )
        else:
            # await interaction.response.defer(thinking=False)

            if threshold is not None:
                threshold = float(threshold.replace(",", "."))
            if time_type is not None:
                time_type = bool(time_type.value)
            if compare is not None:
                compare = bool(compare.value)

            editing_warning = {
                "ticker": ticker,
                "field": field,
                "indicator": indicator,
                "period": period,
                "thresold": threshold,
                "is_greater": compare,
                "is_15_minute": time_type,
                "trigger": True,
            }
            new_warning = old_warning.copy()
            for key, value in editing_warning.items():
                if value is not None:
                    new_warning[key] = value
            print(new_warning)
            nl = "\n"
            embed = discord.Embed(
                title="**Đây là cảnh báo mới sau khi sửa. Bạn có muốn sửa:**"
            )

            embed.add_field(
                name=f'**Mã cảnh báo: {new_warning["_id"]}**',
                value=f"""
    > Mã cổ phiếu: {new_warning["ticker"]}
    > Loại thời gian :{"15 phút" if new_warning["is_15_minute"] else"1 ngày" }
    {"" if (new_warning["field"] is None) else f'> Trường: {new_warning["field"]}'+nl}{"" if (new_warning["indicator"] is None) else f'> Chỉ báo: {new_warning["indicator"]}'+nl}{"" if (new_warning["period"] is None) else f'> Chu kì: {new_warning["period"]}'+nl}> So sánh:{"Lớn hơn" if new_warning["is_greater"] else "Bé hơn"}
    > Ngưỡng:{new_warning["thresold"]}
    """,
                inline=False,
            )

            view = comfirmEditWarning(warning_id=id, new_warning=new_warning)
            await interaction.response.send_message(embed=embed, view=view)


async def setup(client):
    await client.add_cog(Warning(bot=client))
