import discord
from discord import app_commands
from utils.roles import is_mod
from utils.errors import safe_send


async def _unban(interaction: discord.Interaction, user_id: str):
    if not is_mod(interaction.user):
        await safe_send(interaction, "You don't have permission to unban users.", ephemeral=True)
        return
    try:
        user = await interaction.client.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await safe_send(interaction, f"**{user.name}** unbanned.")
    except discord.NotFound:
        await safe_send(interaction, "That user ID wasn't found or isn't banned.", ephemeral=True)
    except discord.Forbidden:
        await safe_send(interaction, "I don't have permission to unban users.", ephemeral=True)
    except ValueError:
        await safe_send(interaction, "Invalid user ID. Must be a number.", ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="unban", description="Unban a user by their ID", guild=guild)
    @app_commands.describe(user_id="The Discord user ID to unban")
    async def slash_unban(interaction: discord.Interaction, user_id: str):
        await _unban(interaction, user_id)
