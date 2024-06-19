import discord
from discord.ext import commands
from discord import app_commands


class Help(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree

    @commands.Cog.listener()
    async def on_ready(self):
        print("help cog loaded")

    @app_commands.command(
        name="danh_sách_lệnh",
        description="danh sách các lệnh và mô tả cách sử dụng trên stock_bot",
    )
    @app_commands.describe()
    async def getAllCommands(self, interaction: discord.Interaction):
        # for cmd in self.bot.commands:
        #     print(cmd)
        #     command_list = "\n".join([f"!{cmd.name} - {cmd.help}" for cmd in commands])
        # embed = discord.Embed(
        #     title="Danh sách các lệnh",
        #     description="\n".join(command_list),
        #     color=discord.Color.blue(),
        # )
        message = (
            "/daily: xem thông tin mới nhất (theo ngày) \n"
            "/latest: xem thông tin mới nhất (theo 15 phút) \n"
            "/daily_chart: xem biểu đồ với dữ liệu theo ngày \n"
            "/oneday_chart: xem biểu đồ với dữ liệu trong 1 ngày nhất định (mặc định là ngày hôm nay) \n"
            "/đọc_cảnh_báo: xem danh sách các cảnh báo đã thiết lập \n"
            "/thêm_cảnh_báo: thêm một cảnh báo về cổ phiếu \n"
            "/xóa_cảnh_báo: xóa đi một cảnh báo đã tạo \n"
            "/sửa_cảnh_báo: sửa một cảnh báo đã tạo \n"
            "/đọc_email: xem email đã thiết lập \n"
            "/thiết_lập_email: thêm hoặc chỉnh sửa email để gửi cảnh báo \n"
            "/xóa_email: xóa email đã thiết lập"
        )
        await interaction.response.send_message(message)


async def setup(client):
    await client.add_cog(Help(bot=client))
