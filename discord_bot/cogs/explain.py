import re
import discord
from discord.ext import commands
from discord import app_commands
from openai import AsyncOpenAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAI
import pandas as pd
import pandas_ta as ta
from pydantic import BaseModel, field_validator, ValidationError, model_validator
from typing import List, ClassVar

from influx_db import get_analaytic_data

print(load_dotenv("../.env"))
df = pd.read_csv("../stock_data_producer/company.csv")
tickers_list = df["ticker"].tolist()


class CommandInput(BaseModel):
    ticker: str
    _allowed_tickers: ClassVar[List[str]] = tickers_list  # List of valid tickers

    @model_validator(mode="before")
    def check(cls, values):
        ticker = values.get("ticker")
        if ticker not in cls._allowed_tickers:
            raise ValueError(
                f"Ticker {ticker} không nằm trong danh sách được hỗ trợ, kiểm tra danh sách các mã cổ phiếu phù hợp trong link sau: https://finance.vietstock.vn/trang-thai-co-phieu/danh-sach-niem-yet"
            )
        return values


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
        try:
            ticker = ticker.upper()
            await interaction.response.defer()
            df = await get_analaytic_data(ticker=ticker)
            df.columns = [re.sub(r"[_\d.]", "", name) for name in df.columns]
            df.index = df.index.tz_convert("Asia/Ho_Chi_minh").strftime("%Y-%m-%d")
            df.reset_index(inplace=True)
            data = df.to_json(orient="records")
            msg = await self.llm.ainvoke(
                [
                    SystemMessage(
                        [
                            {
                                "type": "text",
                                # "text": "Analyze the stock trend from the graph user given, then give response with your analyze and predict trend of the stock and give advice like whether or not to buy or sell the stock. Response with no spare information like how the indicator works,... and also response in Vietnamese and add some markdown component for better visualization but dont use any codeblock or table",
                                "text": """You are a financial analyst. Analyze the following stock data and provide insights on the overall trend, potential trading signals, and market sentiment. The data includes the following columns: _time, close, high, low, volume, SMA, MACD, RSI, STOCHk, OBV, BBL, BBM, BBU, and ATRr in JSON format. 1. **Overall Trend**: - Examine the closing prices and Simple Moving Average (SMA) to determine the overall trend of the stock. - Analyze the MACD values to understand the momentum and potential trend reversals. 2. **Trading Signals**: - Use the Relative Strength Index (RSI) to identify overbought or oversold conditions. - Evaluate the Stochastic Oscillator (STOCHk) for additional momentum and reversal signals. 3. **Volume Analysis**: - Assess the On-Balance Volume (OBV) to understand the buying and selling pressure. 4. **Volatility**: - Interpret the Bollinger Bands (BBL, BBM, BBU) to gauge market volatility and potential breakouts. - Use the Average True Range (ATRr) to measure market volatility. 5. **Key Support and Resistance Levels**: - Identify key support and resistance levels based on high and low prices. Provide a detailed analysis of the stock's performance over time, highlighting any significant patterns or signals that could inform trading decisions. Use the provided data to support your analysis. Predict trend of the stock and give advice like whether or not to buy or sell the stock right at that moment The stock data is given by user Response in Vietnamese and add some markdown component for better visualization but dont use any codeblock or table or heading. Please provide your analysis.""",
                            }
                        ]
                    ),
                    HumanMessage(
                        content=[
                            {
                                "type": "text",
                                "text": data,
                            },
                        ]
                    ),
                ]
            )
            text = msg.content
            split_index = text.rfind("\n", 0, 1800)
            if split_index == -1:
                return await interaction.followup.send("Đã có lỗi xảy ra")
            part1 = text[:split_index].strip()
            part2 = text[split_index + 1 :].strip()
            await interaction.followup.send(content=part1)
            await interaction.followup.send(content=part2)
        except Exception as e:
            print(e)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.explain.name, type=self.explain.type)


async def setup(bot):
    await bot.add_cog(Explain(bot=bot))
