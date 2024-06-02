import discord

from mongo_db import deleteWarning


class comfirmDeleteWarning(discord.ui.View):
    message: discord.Message | None = None

    def __init__(self, warning_id: str, timeout: float = 60.0) -> None:
        super().__init__(timeout=timeout)
        self.warning_id = warning_id

    @discord.ui.button(label="Xác nhận", style=discord.ButtonStyle.success)
    async def ComfirmButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await deleteWarning(self.warning_id)
        await interaction.response.edit_message(
            content="Cảnh báo đã được xóa thành công", view=None
        )

    @discord.ui.button(label="Hủy", style=discord.ButtonStyle.danger)
    async def DeferButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(content="Lệnh đã hủy", view=None)
