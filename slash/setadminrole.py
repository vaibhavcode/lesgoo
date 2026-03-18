import discord
from discord import app_commands
from utils.roles import add_admin_role
from utils.errors import safe_send


async def _setadminrole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await safe_send(interaction, "Only users with the Discord Administrator permission can assign admin roles.", ephemeral=True)
        return
    add_admin_role(interaction.guild.id, role.id)
    await safe_send(interaction, f"**{role.name}** added as an admin role.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="setadminrole", description="Assign an admin role (Discord admin only)", guild=guild)
    @app_commands.describe(role="Role to assign as admin")
    async def slash_setadminrole(interaction: discord.Interaction, role: discord.Role):
        await _setadminrole(interaction, role)
