import discord
from utils.memory import clear_user_memory
from utils.errors import safe_send


async def _clear(interaction: discord.Interaction):
    clear_user_memory(interaction.user.id)
    await safe_send(interaction, "Memory cleared. Aarshi has no idea who you are anymore.")


def setup(bot, guild):
    @bot.tree.command(name="clear", description="Wipe your conversation history with Aarshi", guild=guild)
    async def slash_clear(interaction: discord.Interaction):
        await _clear(interaction)
