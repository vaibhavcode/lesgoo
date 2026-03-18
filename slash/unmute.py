import discord
from discord import app_commands
from utils.roles import is_mod


async def _unmute(interaction: discord.Interaction, user: discord.Member):
    if not is_mod(interaction.user):
        await interaction.response.send_message("You don't have permission to unmute users.", ephemeral=True)
        return
    try:
        await user.timeout(None)
        embed = discord.Embed(title="User unmuted", color=discord.Color.green())
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Mod", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to unmute that user.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="unmute", description="Remove a timeout from a user", guild=guild)
    @app_commands.describe(user="User to unmute")
    async def slash_unmute(interaction: discord.Interaction, user: discord.Member):
        await _unmute(interaction, user)
