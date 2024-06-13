import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import discord
from discord.ext import commands, tasks
from discord import app_commands, File, Attachment
from discord.app_commands import Choice
from dotenv import load_dotenv, dotenv_values
from typing import Literal
import os
from View.edit_warning import comfirmEditWarning
from View.delete_warning import comfirmDeleteWarning

# from influx_db import (
#     get_latest_data,
#     get_latest_daily_data,
#     get_all_time_data,
#     get_single_day_data,
# )
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

print(load_dotenv("../.env"))
# consumer = Consumer(
#     {
#         "bootstrap.servers": "pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092",
#         "security.protocol": "SASL_SSL",
#         "sasl.mechanism": "PLAIN",
#         "sasl.username": "HGLHHLIGH5YQYKVX",
#         "sasl.password": "gX5Smh7m7hoFTvIxUGPL9hwNJmgo1nQZBr/nHpFXD56jNm52m8i5C5Dor0/XMiD9",
#         "group.id": "stock_price_group",
#         "auto.offset.reset": "latest",  # Start from the latest message
#         "client.id": socket.gethostname(),
#         "debug": "security,broker,protocol",
#     }
# )

# consumer.subscribe(["stock_warning"])


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        wrapped = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, wrapped)

    return wrapper


class Warning(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree

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
        thresold="float",
    )
    @app_commands.rename(
        ticker="mã_cổ_phiếu",
        field="trường",
        indicator="chỉ_báo",
        time_type="loại_thời_gian",
        period="chu_kì",
        compare="so_sánh",
        thresold="ngưỡng",
    )
    async def add_warning(
        self,
        interaction: discord.Interaction,
        ticker: str,
        time_type: Choice[int],
        compare: Choice[int],
        thresold: str,
        period: int | None = None,
        field: str = None,
        indicator: str = None,
    ):
        thresold = float(thresold.replace(",", "."))
        user_id = interaction.user.id
        time_type = bool(time_type.value)
        compare = bool(compare.value)
        await addWarning(
            user_id=user_id,
            ticker=ticker,
            field=field,
            indicator=indicator,
            time_type=time_type,
            period=period,
            compare=compare,
            thresold=thresold,
        )
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
        thresold="float",
    )
    @app_commands.rename(
        id="mã_cảnh_báo",
        ticker="mã_cổ_phiếu",
        field="trường",
        indicator="chỉ_báo",
        time_type="loại_thời_gian",
        period="chu_kì",
        compare="so_sánh",
        thresold="ngưỡng",
    )
    async def edit_warning(
        self,
        interaction: discord.Interaction,
        id: str,
        ticker: str = None,
        time_type: Choice[int] = None,
        compare: Choice[int] = None,
        thresold: str = None,
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
            await interaction.response.defer()

            if thresold is not None:
                thresold = float(thresold.replace(",", "."))
            if time_type is not None:
                time_type = bool(time_type.value)
            if compare is not None:
                compare = bool(compare.value)

            editing_warning = {
                "ticker": ticker,
                "field": field,
                "indicator": indicator,
                "period": period,
                "thresold": thresold,
                "is_greater": compare,
                "is_15_minute": time_type,
                "trigger": True,
            }

            new_warning = old_warning.copy()
            for key, value in editing_warning.items():
                if value is not None:
                    new_warning[key] = value

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
            await interaction.followup.send(embed=embed, view=view)


async def setup(client):
    await client.add_cog(Warning(bot=client))
