import discord
from discord import app_commands
from datetime import timedelta
from utils.roles import is_mod
from utils.errors import safe_send


async def _mute(interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str):
    if not is_mod(interaction.user):
        await safe_send(interaction, "You don't have permission to mute users.", ephemeral=True)
        return
    if user == interaction.client.user:
        await safe_send(interaction, "Mute *me*? Try it.", ephemeral=True)
        return
    if user.guild_permissions.administrator:
        await safe_send(interaction, "I can't mute an administrator.", ephemeral=True)
        return
    try:
        await user.timeout(timedelta(minutes=minutes), reason=reason)
        await safe_send(interaction, f"**{user.display_name}** muted for {minutes} minute(s). Reason: {reason}")
    except discord.Forbidden:
        await safe_send(interaction, "I don't have permission to mute that user.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="mute", description="Timeout a user", guild=guild)
    @app_commands.describe(user="User to mute", minutes="Duration in minutes", reason="Reason for the mute")
    async def slash_mute(interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str = "No reason provided"):
        await _mute(interaction, user, minutes, reason)
