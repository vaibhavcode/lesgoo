import discord
from discord import app_commands
from utils.roles import is_mod


async def _unban(interaction: discord.Interaction, user_id: str):
    if not is_mod(interaction.user):
        await interaction.response.send_message("You don't have permission to unban users.", ephemeral=True)
        return
    try:
        user = await interaction.client.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        embed = discord.Embed(title="User unbanned", color=discord.Color.green())
        embed.add_field(name="User", value=f"{user.name}", inline=True)
        embed.add_field(name="Mod", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except discord.NotFound:
        await interaction.response.send_message("That user ID wasn't found or isn't banned.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to unban users.", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Invalid user ID. Must be a number.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="unban", description="Unban a user by their ID", guild=guild)
    @app_commands.describe(user_id="The Discord user ID to unban")
    async def slash_unban(interaction: discord.Interaction, user_id: str):
        await _unban(interaction, user_id)
