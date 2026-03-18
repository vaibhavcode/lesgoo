import discord
from discord import app_commands
from utils.roles import is_admin, add_mod_role


async def _setmodrole(interaction: discord.Interaction, role: discord.Role):
    if not is_admin(interaction.user):
        await interaction.response.send_message("You need to be an admin to assign mod roles.", ephemeral=True)
        return
    add_mod_role(interaction.guild.id, role.id)
    await interaction.response.send_message(f"**{role.name}** has been added as a mod role.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="setmodrole", description="Assign a mod role (admin only)", guild=guild)
    @app_commands.describe(role="Role to assign as mod")
    async def slash_setmodrole(interaction: discord.Interaction, role: discord.Role):
        await _setmodrole(interaction, role)
