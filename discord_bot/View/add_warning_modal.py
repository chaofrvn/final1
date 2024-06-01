import discord
from discord.ui import TextInput, Modal, View, Button, button


class addWarningModal(Modal):
    def __init__(self, previous_data=None):
        super().__init__(title="Add Warning")

        # Initialize TextInput fields with previous data if available
        self.ticker = TextInput(
            label="ticker",
            placeholder="BID",
            default=(
                previous_data["ticker"]
                if previous_data and "ticker" in previous_data
                else ""
            ),
        )

        self.time_type = TextInput(
            label="time_type",
            placeholder="1D 15m",
            default=(
                previous_data["time_type"]
                if previous_data and "time_type" in previous_data
                else ""
            ),
        )
        self.compare = TextInput(
            label="compare",
            placeholder="GREATER LESS",
            default=(
                previous_data["compare"]
                if previous_data and "compare" in previous_data
                else ""
            ),
        )
        self.thresold = TextInput(
            label="thresold",
            placeholder="thresold",
            default=(
                previous_data["thresold"]
                if previous_data and "thresold" in previous_data
                else ""
            ),
        )
        # Add TextInput fields to the modal
        self.add_item(self.ticker)
        self.add_item(self.time_type)
        self.add_item(self.compare)
        self.add_item(self.thresold)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(
            SecondPage(
                # {
                #     "ticker": str(self.ticker),
                #     "time_type": str(self.time_type),
                #     "compare": str(self.compare),
                #     "thresold": str(self.thresold),
                #     "indicator": "",
                #     "field": "",
                #     "period": "",
                # }
            )
        )
        await interaction.response.send_message(
            str(
                {
                    "ticker": str(self.ticker),
                    "time_type": str(self.time_type),
                    "compare": str(self.compare),
                    "thresold": str(self.thresold),
                    "indicator": "",
                    "field": "",
                    "period": "",
                }
            )
        )


class SecondPage(Modal, title="test"):
    def __init__(self, previous_data=None):
        self.previous_data = previous_data
        super().__init__(title="test")
        print("here")
        # Initialize TextInput fields with previous data if available
        self.indicator = TextInput(
            label="indicator",
            placeholder="ma ema so",
            required=False,
            default=(
                previous_data["indicator"]
                if previous_data and "indicator" in previous_data
                else ""
            ),
        )
        self.field = TextInput(
            label="field",
            placeholder="close",
            required=False,
            default=(
                previous_data["field"]
                if previous_data and "field" in previous_data
                else ""
            ),
        )
        self.period = TextInput(
            label="period",
            placeholder="14",
            required=False,
            default=(
                previous_data["period"]
                if previous_data and "period" in previous_data
                else ""
            ),
        )

        # Add TextInput fields to the modal
        self.add_item(self.indicator)
        self.add_item(self.period)
        self.add_item(self.field)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            {
                "field": self.field,
                "indicator": self.indicator,
                "period": self.period,
                **self.previous_data,
            }
        )


class ErrorView(View):
    def __init__(self):
        super().__init__()

    @button(label="Continue", style=discord.ButtonStyle.primary)
    async def continue_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(addWarningModal())

    @button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Operation cancelled.", ephemeral=True)
