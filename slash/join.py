import discord
from utils.errors import safe_send, user_not_in_voice


async def _join(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await user_not_in_voice(interaction)
        return
    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client
    if vc and vc.is_connected():
        await vc.move_to(channel)
    else:
        await channel.connect()
    await safe_send(interaction, f"Joined **{channel.name}**.")


def setup(bot, guild):
    @bot.tree.command(name="join", description="Invite Aarshi into your voice channel", guild=guild)
    async def slash_join(interaction: discord.Interaction):
        await _join(interaction)
