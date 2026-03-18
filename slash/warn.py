import discord
from discord import app_commands
from utils.roles import is_mod
from utils.warnings import add_warning


async def _warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not is_mod(interaction.user):
        await interaction.response.send_message("You don't have permission to warn users.", ephemeral=True)
        return
    if user == interaction.client.user:
        await interaction.response.send_message("Warn *me*? Absolutely not.", ephemeral=True)
        return
    count = add_warning(interaction.guild.id, user.id, reason, interaction.user.name)
    embed = discord.Embed(title="Warning issued", color=discord.Color.yellow())
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Mod", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=f"This is warning #{count} for this user.")
    await interaction.response.send_message(embed=embed)


def setup(bot, guild):
    @bot.tree.command(name="warn", description="Warn a user", guild=guild)
    @app_commands.describe(user="User to warn", reason="Reason for the warning")
    async def slash_warn(interaction: discord.Interaction, user: discord.Member, reason: str):
        await _warn(interaction, user, reason)
