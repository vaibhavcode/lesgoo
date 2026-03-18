import discord
from discord import app_commands
from utils.roles import is_mod


async def _kick(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not is_mod(interaction.user):
        await interaction.response.send_message("You don't have permission to kick users.", ephemeral=True)
        return
    if user == interaction.client.user:
        await interaction.response.send_message("Kick *me*? Absolutely not.", ephemeral=True)
        return
    if user.guild_permissions.administrator:
        await interaction.response.send_message("I can't kick an administrator.", ephemeral=True)
        return
    try:
        await user.kick(reason=reason)
        embed = discord.Embed(title="User kicked", color=discord.Color.red())
        embed.add_field(name="User", value=f"{user.name}", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Mod", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to kick that user.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="kick", description="Kick a user from the server", guild=guild)
    @app_commands.describe(user="User to kick", reason="Reason for the kick")
    async def slash_kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await _kick(interaction, user, reason)
