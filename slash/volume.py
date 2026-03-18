import discord
from discord import app_commands
from utils.music import get_queue
from utils.errors import safe_send, not_in_voice


async def _volume(interaction: discord.Interaction, level: int):
    if not 0 <= level <= 100:
        await safe_send(interaction, "Volume must be between 0 and 100.", ephemeral=True)
        return

    vc = interaction.guild.voice_client

    if vc is None or not vc.is_connected():
        await not_in_voice(interaction)
        return

    mq = get_queue(interaction.guild.id)
    mq.volume = level / 100.0

    # Apply immediately if something is playing
    if vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
        vc.source.volume = mq.volume

    await safe_send(interaction, f"Volume set to **{level}%**.")


def setup(bot, guild):
    @bot.tree.command(name="volume", description="Adjust playback volume", guild=guild)
    @app_commands.describe(level="Volume level from 0 to 100")
    async def slash_volume(interaction: discord.Interaction, level: int):
        await _volume(interaction, level)
