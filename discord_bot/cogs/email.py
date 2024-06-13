import os
import sys
import inspect
import re

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import discord
from discord.ext import commands
from discord import app_commands
from mongo_db import setEmail, getEmail, deleteEmail


class Email(commands.Cog):
    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree

    @commands.Cog.listener()
    async def on_ready(self):
        print("Email cog loaded")

    @app_commands.command(
        name="thiết_lập_email",
        description="Thêm hoặc chỉnh sửa email",
    )
    @app_commands.describe(email="Địa chỉ email bạn sử dụng")
    async def upsertEmail(self, interaction: discord.Interaction, email: str):

        if not re.match(self.EMAIL_REGEX, email):
            return await interaction.response.send_message("Email không hợp lệ")

        result = await setEmail(interaction.user.id, email)
        return await interaction.response.send_message(result)

    @app_commands.command(
        name="xóa_email",
        description="Xóa email",
    )
    @app_commands.describe()
    async def DeleteEmail(self, interaction: discord.Interaction):

        result = await deleteEmail(interaction.user.id)
        await interaction.response.send_message(result)

    @app_commands.command(
        name="đọc_email",
        description="Đọc email",
    )
    @app_commands.describe()
    async def ReadEmail(self, interaction: discord.Interaction):

        result = await getEmail(interaction.user.id)
        await interaction.response.send_message(result)


async def setup(bot):
    await bot.add_cog(Email(bot=bot))
