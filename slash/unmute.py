import discord
from discord import app_commands
from utils.roles import is_mod
from utils.errors import safe_send


async def _unmute(interaction: discord.Interaction, user: discord.Member):
    if not is_mod(interaction.user):
        await safe_send(interaction, "You don't have permission to unmute users.", ephemeral=True)
        return
    try:
        await user.timeout(None)
        await safe_send(interaction, f"**{user.display_name}** unmuted.")
    except discord.Forbidden:
        await safe_send(interaction, "I don't have permission to unmute that user.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="unmute", description="Remove a timeout from a user", guild=guild)
    @app_commands.describe(user="User to unmute")
    async def slash_unmute(interaction: discord.Interaction, user: discord.Member):
        await _unmute(interaction, user)
