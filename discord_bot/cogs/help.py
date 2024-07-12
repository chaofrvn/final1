import discord
from discord.ext import commands
from discord import app_commands


class Help(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree

    @commands.Cog.listener()
    async def on_ready(self):
        print("Help cog loaded")

    @app_commands.command(
        name="danh_sách_lệnh",
        description="danh sách các lệnh và mô tả cách sử dụng trên stock_bot",
    )
    @app_commands.describe()
    async def getAllCommands(self, interaction: discord.Interaction):
        message = (
            "- /daily: xem thông tin mới nhất (theo ngày) \n"
            "- /latest: xem thông tin mới nhất (theo 15 phút) \n"
            "- /daily_chart: xem biểu đồ với dữ liệu theo ngày \n"
            "- /oneday_chart: xem biểu đồ với dữ liệu trong 1 ngày nhất định (mặc định là ngày hôm nay) \n"
            "- /đọc_cảnh_báo: xem danh sách các cảnh báo đã thiết lập \n"
            "- /thêm_cảnh_báo: thêm một cảnh báo về cổ phiếu \n"
            "- /xóa_cảnh_báo: xóa đi một cảnh báo đã tạo \n"
            "- /sửa_cảnh_báo: sửa một cảnh báo đã tạo \n"
            "- /đọc_email: xem email đã thiết lập \n"
            "- /thiết_lập_email: thêm hoặc chỉnh sửa email để gửi cảnh báo \n"
            "- /xóa_email: xóa email đã thiết lập \n"
            "- /dự_đoán: Đưa ra các dự đoán về tương lai của cổ phiếu"
        )
        await interaction.response.send_message(message)

    @app_commands.command(
        name="danh_sách_chỉ_báo",
        description="danh sách các chỉ báo có sẵn trong stock_bot",
    )
    @app_commands.describe()
    async def getAllIndicators(self, interaction: discord.Interaction):
        indicators_description = (
            "- ma: Moving Average -  Giá trị trung bình liên tục.\n"
            "- ema: Exponential Moving Average - Trung bình động đặt nhiều trọng số hơn vào các giá trị gần đây để phản ánh biến động giá mới nhất.\n"
            "- macd: Moving Average Convergence Divergence - Chỉ báo thể hiện mối quan hệ giữa hai đường trung bình động của giá chứng khoán.\n"
            "- vwap: Volume Weighted Average Price - Giá trung bình của chứng khoán được tính dựa trên cả giá và khối lượng giao dịch.\n"
            "- rsi: Relative Strength Index - Chỉ báo động lượng đo lường tốc độ và sự thay đổi của các biến động giá.\n"
            "- stoch: Stochastic Oscillator - Chỉ báo động lượng so sánh giá đóng cửa của chứng khoán với một phạm vi giá trong một khoảng thời gian nhất định.\n"
            "- atr: Average True Range - Chỉ báo đo lường mức độ biến động trung bình của chứng khoán trong một khoảng thời gian nhất định.\n"
            "- obv: On-Balance Volume - Chỉ báo động lượng sử dụng khối lượng giao dịch để dự đoán những thay đổi trong giá chứng khoán.\n"
            "- roc: Price Rate of Change - Chỉ báo đo lường tỷ lệ phần trăm thay đổi của giá chứng khoán trong một khoảng thời gian nhất định.\n"
        )
        await interaction.response.send_message(indicators_description)


async def setup(client):
    await client.add_cog(Help(bot=client))
