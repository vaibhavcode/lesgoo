import discord
from discord import app_commands
from utils.roles import is_mod
from utils.warnings import get_warnings


async def _warnings(interaction: discord.Interaction, user: discord.Member):
    if not is_mod(interaction.user):
        await interaction.response.send_message("You don't have permission to view warnings.", ephemeral=True)
        return
    records = get_warnings(interaction.guild.id, user.id)
    embed = discord.Embed(title=f"Warnings for {user.display_name}", color=discord.Color.yellow())
    if not records:
        embed.description = "No warnings on record."
    else:
        for i, w in enumerate(records, 1):
            embed.add_field(
                name=f"Warning #{i} — {w['timestamp'][:10]}",
                value=f"**Reason:** {w['reason']}\n**Mod:** {w['mod']}",
                inline=False
            )
    await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="warnings", description="View warnings for a user", guild=guild)
    @app_commands.describe(user="User to check warnings for")
    async def slash_warnings(interaction: discord.Interaction, user: discord.Member):
        await _warnings(interaction, user)
