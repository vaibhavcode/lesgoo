import discord
from utils.music import get_queue
from utils.errors import safe_send, not_in_voice


async def _skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc is None or not vc.is_connected():
        await not_in_voice(interaction)
        return
    if not vc.is_playing() and not vc.is_paused():
        await safe_send(interaction, "Nothing is playing.")
        return
    mq = get_queue(interaction.guild.id)
    was_looping = mq.loop
    mq.loop = False
    mq.current = None
    vc.stop()
    if was_looping:
        await safe_send(interaction, "Loop disabled and track skipped.")
    else:
        await safe_send(interaction, "Skipped.")


def setup(bot, guild):
    @bot.tree.command(name="skip", description="Skip the current track", guild=guild)
    async def slash_skip(interaction: discord.Interaction):
        await _skip(interaction)
