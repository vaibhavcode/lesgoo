import discord
from discord import app_commands
from utils.roles import is_admin, add_mod_role
from utils.errors import safe_send


async def _setmodrole(interaction: discord.Interaction, role: discord.Role):
    if not is_admin(interaction.user):
        await safe_send(interaction, "You need to be an admin to assign mod roles.", ephemeral=True)
        return
    add_mod_role(interaction.guild.id, role.id)
    await safe_send(interaction, f"**{role.name}** added as a mod role.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="setmodrole", description="Assign a mod role (admin only)", guild=guild)
    @app_commands.describe(role="Role to assign as mod")
    async def slash_setmodrole(interaction: discord.Interaction, role: discord.Role):
        await _setmodrole(interaction, role)
