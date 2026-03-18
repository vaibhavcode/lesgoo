import discord
from utils.roles import is_admin, get_mod_roles, get_admin_roles


async def _modroles(interaction: discord.Interaction):
    if not is_admin(interaction.user):
        await interaction.response.send_message("You don't have permission to view role assignments.", ephemeral=True)
        return
    def fmt(role_ids):
        if not role_ids:
            return "None assigned"
        roles = [interaction.guild.get_role(rid) for rid in role_ids]
        return "\n".join(f"• {r.name} (`{r.id}`)" for r in roles if r) or "None found"
    embed = discord.Embed(title="Assigned Roles", color=discord.Color.blurple())
    embed.add_field(name="Mod roles", value=fmt(get_mod_roles(interaction.guild.id)), inline=False)
    embed.add_field(name="Admin roles", value=fmt(get_admin_roles(interaction.guild.id)), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="modroles", description="View assigned mod and admin roles", guild=guild)
    async def slash_modroles(interaction: discord.Interaction):
        await _modroles(interaction)
