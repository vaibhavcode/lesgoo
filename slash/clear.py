import discord
from utils.memory import clear_user_memory


async def _clear(interaction: discord.Interaction):
    clear_user_memory(interaction.user.id)
    await interaction.response.send_message(
        f"Memory cleared for **{interaction.user.display_name}**. Aarshi has no idea who you are anymore."
    )


def setup(bot, guild):
    @bot.tree.command(name="clear", description="Wipe your conversation history with Aarshi", guild=guild)
    async def slash_clear(interaction: discord.Interaction):
        await _clear(interaction)
