import discord
from utils.errors import safe_send, not_in_voice


async def _resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc is None or not vc.is_connected():
        await not_in_voice(interaction)
        return

    if not vc.is_paused():
        await safe_send(interaction, "Nothing is paused.", ephemeral=True)
        return

    vc.resume()
    await safe_send(interaction, "Resumed.")


def setup(bot, guild):
    @bot.tree.command(name="resume", description="Resume the paused track", guild=guild)
    async def slash_resume(interaction: discord.Interaction):
        await _resume(interaction)
