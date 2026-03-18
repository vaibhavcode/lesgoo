import discord
from discord import app_commands
from utils.roles import is_mod
from utils.errors import safe_send


async def _purge(interaction: discord.Interaction, amount: int):
    if not is_mod(interaction.user):
        await safe_send(interaction, "You don't have permission to purge messages.", ephemeral=True)
        return
    if not 1 <= amount <= 100:
        await safe_send(interaction, "Amount must be between 1 and 100.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Deleted **{len(deleted)}** message(s).", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="purge", description="Delete multiple messages from this channel", guild=guild)
    @app_commands.describe(amount="Number of messages to delete (max 100)")
    async def slash_purge(interaction: discord.Interaction, amount: int):
        await _purge(interaction, amount)
