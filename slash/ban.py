import discord
from discord import app_commands
from utils.roles import is_mod


async def _ban(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not is_mod(interaction.user):
        await interaction.response.send_message("You don't have permission to ban users.", ephemeral=True)
        return
    if user == interaction.client.user:
        await interaction.response.send_message("Ban *me*? You wouldn't dare.", ephemeral=True)
        return
    if user.guild_permissions.administrator:
        await interaction.response.send_message("I can't ban an administrator.", ephemeral=True)
        return
    try:
        await user.ban(reason=reason, delete_message_days=0)
        embed = discord.Embed(title="User banned", color=discord.Color.dark_red())
        embed.add_field(name="User", value=f"{user.name}", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Mod", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to ban that user.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="ban", description="Ban a user from the server", guild=guild)
    @app_commands.describe(user="User to ban", reason="Reason for the ban")
    async def slash_ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await _ban(interaction, user, reason)
