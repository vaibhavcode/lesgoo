import discord
from discord import app_commands
from utils.roles import is_mod
from utils.warnings import add_warning
from utils.errors import safe_send


async def _warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not is_mod(interaction.user):
        await safe_send(interaction, "You don't have permission to warn users.", ephemeral=True)
        return
    if user == interaction.client.user:
        await safe_send(interaction, "Warn *me*? Absolutely not.", ephemeral=True)
        return
    count = add_warning(interaction.guild.id, user.id, reason, interaction.user.name)
    await safe_send(interaction, f"Warning #{count} issued to **{user.display_name}**. Reason: {reason}")


def setup(bot, guild):
    @bot.tree.command(name="warn", description="Warn a user", guild=guild)
    @app_commands.describe(user="User to warn", reason="Reason for the warning")
    async def slash_warn(interaction: discord.Interaction, user: discord.Member, reason: str):
        await _warn(interaction, user, reason)
