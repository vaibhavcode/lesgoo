import discord
from discord import app_commands
from datetime import timedelta
from utils.roles import is_mod


async def _mute(interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str):
    if not is_mod(interaction.user):
        await interaction.response.send_message("You don't have permission to mute users.", ephemeral=True)
        return
    if user == interaction.client.user:
        await interaction.response.send_message("Mute *me*? Try it.", ephemeral=True)
        return
    if user.guild_permissions.administrator:
        await interaction.response.send_message("I can't mute an administrator.", ephemeral=True)
        return
    try:
        await user.timeout(timedelta(minutes=minutes), reason=reason)
        embed = discord.Embed(title="User muted", color=discord.Color.orange())
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Duration", value=f"{minutes} minute(s)", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Mod", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to mute that user.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="mute", description="Timeout a user", guild=guild)
    @app_commands.describe(user="User to mute", minutes="Duration in minutes", reason="Reason for the mute")
    async def slash_mute(interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str = "No reason provided"):
        await _mute(interaction, user, minutes, reason)
