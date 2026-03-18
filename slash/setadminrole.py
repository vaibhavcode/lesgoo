import discord
from discord import app_commands
from utils.roles import add_admin_role


async def _setadminrole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Only users with the Discord Administrator permission can assign admin roles.", ephemeral=True
        )
        return
    add_admin_role(interaction.guild.id, role.id)
    await interaction.response.send_message(f"**{role.name}** has been added as an admin role.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="setadminrole", description="Assign an admin role (Discord admin only)", guild=guild)
    @app_commands.describe(role="Role to assign as admin")
    async def slash_setadminrole(interaction: discord.Interaction, role: discord.Role):
        await _setadminrole(interaction, role)
