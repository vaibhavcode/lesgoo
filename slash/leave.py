import discord
from utils.errors import safe_send, not_in_voice


async def _leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc is None or not vc.is_connected():
        await not_in_voice(interaction)
        return
    channel_name = vc.channel.name
    await vc.disconnect()
    await safe_send(interaction, f"Left **{channel_name}**.")


def setup(bot, guild):
    @bot.tree.command(name="leave", description="Kick Aarshi out of the voice channel", guild=guild)
    async def slash_leave(interaction: discord.Interaction):
        await _leave(interaction)
