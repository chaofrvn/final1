import discord
from discord.ext import commands
from discord import app_commands
from openai import AsyncOpenAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAI
import pandas as pd
import pandas_ta as ta

print(load_dotenv("../.env"))


class Explain(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.llm = ChatOpenAI(temperature=0.5, model="gpt-4o", max_tokens=4095)
        self.explain = app_commands.ContextMenu(
            name="Giải thích",
            callback=self.explain_context_menu,
        )
        self.bot.tree.add_command(self.explain)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Explain cog loaded")

    async def explain_context_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        if (
            message.author != self.bot.user
            or len(message.embeds) == 0
            or message.embeds[0].title != "Đây là biểu đồ của bạn:"
        ):
            await interaction.response.send_message(
                "Tin nhắn cần là biểu đồ của bot để có thể phân tích"
            )
        else:
            await interaction.response.defer()
            image_url = message.embeds[0].image.proxy_url
            # print(image_url)
            msg = await self.llm.ainvoke(
                [
                    SystemMessage(
                        [
                            {
                                "type": "text",
                                "text": "Analyze the stock trend from the graph user given, then give response with your analyze and predict trend of the stock and give advice like whether or not to buy or sell the stock. Response with no spare information like how the indicator works,... and also response in Vietnamese and add some markdown component for better visualization but dont use any codeblock or table",
                            }
                        ]
                    ),
                    HumanMessage(
                        content=[
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                        ]
                    ),
                ]
            )
            print(msg.content)
            # print(image)
            # print(image.proxy_url)
            # print(image.url)
            embed = discord.Embed()
            embed.set_image(url=image_url)
            await interaction.followup.send(content=msg.content, embed=embed)

    @app_commands.command(name="dự_đoán", description="Dự đoán giá trị của cổ phiếu")
    @app_commands.describe(ticker="Mã cổ phiếu cần dự đoán")
    @app_commands.rename(ticker="mã_cổ_phiếu")
    async def predict(self, interaction: discord.Interaction, ticker: str):

        await interaction.response.send_message("chua viet")

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.explain.name, type=self.explain.type)


async def setup(bot):
    await bot.add_cog(Explain(bot=bot))
