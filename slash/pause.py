import discord
from utils.errors import safe_send, not_in_voice


async def _pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc is None or not vc.is_connected():
        await not_in_voice(interaction)
        return

    if vc.is_paused():
        await safe_send(interaction, "Already paused.", ephemeral=True)
        return

    if not vc.is_playing():
        await safe_send(interaction, "Nothing is playing.", ephemeral=True)
        return

    vc.pause()
    await safe_send(interaction, "Paused.")


def setup(bot, guild):
    @bot.tree.command(name="pause", description="Pause the current track", guild=guild)
    async def slash_pause(interaction: discord.Interaction):
        await _pause(interaction)
