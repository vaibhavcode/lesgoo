import discord
from utils.music import get_queue
from utils.errors import safe_send, not_in_voice
from utils.logger import get_logger

logger = get_logger("slash.stop")


async def _stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc is None or not vc.is_connected():
        await not_in_voice(interaction)
        return

    mq = get_queue(interaction.guild.id)
    mq.clear()
    mq.loop = False

    if vc.is_playing() or vc.is_paused():
        vc.stop()

    await safe_send(interaction, "Stopped playback and cleared the queue.")
    logger.info(f"Playback stopped in guild {interaction.guild.id}")


def setup(bot, guild):
    @bot.tree.command(name="stop", description="Stop music and clear the queue", guild=guild)
    async def slash_stop(interaction: discord.Interaction):
        await _stop(interaction)
