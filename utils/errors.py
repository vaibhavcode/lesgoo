import discord
import traceback
from utils.logger import slash_logger


# ---- Standard error responses ----

async def not_dev(interaction: discord.Interaction):
    await safe_send(interaction, "You're not the developer.", ephemeral=True)


async def not_mod(interaction: discord.Interaction):
    await safe_send(interaction, "You don't have permission to use this command.", ephemeral=True)


async def not_admin(interaction: discord.Interaction):
    await safe_send(interaction, "You need to be an admin to use this command.", ephemeral=True)


async def not_in_voice(interaction: discord.Interaction):
    await safe_send(interaction, "I'm not in a voice channel. Use `/join` first.", ephemeral=True)


async def user_not_in_voice(interaction: discord.Interaction):
    await safe_send(interaction, "You need to be in a voice channel first.", ephemeral=True)


async def cannot_target_self(interaction: discord.Interaction):
    await safe_send(interaction, "You can't use this command on me.", ephemeral=True)


async def cannot_target_admin(interaction: discord.Interaction):
    await safe_send(interaction, "I can't use this command on an administrator.", ephemeral=True)


async def missing_permissions(interaction: discord.Interaction, action: str):
    await safe_send(interaction, f"I don't have permission to {action}.", ephemeral=True)


async def unexpected_error(interaction: discord.Interaction, error: Exception, context: str = ""):
    tb = traceback.format_exc()
    slash_logger.error(f"Unexpected error in {context or interaction.command.name}: {error}\n{tb}")
    await safe_send(
        interaction,
        "Something went wrong. It's *definitely* not my fault. Try again.",
        ephemeral=True
    )


# ---- Safe send helper ----
# Handles the case where interaction has already been responded to

async def safe_send(interaction: discord.Interaction, content: str = None, ephemeral: bool = False, embed: discord.Embed = None):
    try:
        if interaction.response.is_done():
            await interaction.followup.send(content=content, ephemeral=ephemeral, embed=embed)
        else:
            await interaction.response.send_message(content=content, ephemeral=ephemeral, embed=embed)
    except discord.NotFound:
        slash_logger.warning(f"Interaction expired before response could be sent in {interaction.command.name if interaction.command else 'unknown'}")
    except Exception as e:
        slash_logger.error(f"Failed to send error response: {e}")
