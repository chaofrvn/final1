import discord
from discord.ext import commands
from discord import app_commands
from openai import AsyncOpenAI
from dotenv import load_dotenv

print(load_dotenv("../.env"))


class Explain(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = AsyncOpenAI()
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
            print(image_url)
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze the stock trend from the graph user given, then give response with your analyze and predict trend of the stock and give advice like whether or not to buy or sell the stock. Response with no spare information like how the indicator works,... and also response in Vietnamese and add some markdown component for better visualization but dont use any codeblock or table",
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                },
                            },
                        ],
                    },
                ],
                max_tokens=4096,
                timeout=100,
            )
            print(response)
            # print(image)
            # print(image.proxy_url)
            # print(image.url)
            embed = discord.Embed()
            embed.set_image(url=image_url)
            await interaction.followup.send(
                content=response.choices[0].message.content, embed=embed
            )

    @app_commands.command(name="dự_đoán")
    async def predict(self, interaction: discord.Interaction):
        await interaction.response.send_message("chua viet")

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.explain.name, type=self.explain.type)


async def setup(bot):
    await bot.add_cog(Explain(bot=bot))
