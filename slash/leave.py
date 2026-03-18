import discord


async def _leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc is None or not vc.is_connected():
        await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)
        return
    channel_name = vc.channel.name
    await vc.disconnect()
    await interaction.response.send_message(f"Left **{channel_name}**.")


def setup(bot, guild):
    @bot.tree.command(name="leave", description="Kick Aarshi out of the voice channel", guild=guild)
    async def slash_leave(interaction: discord.Interaction):
        await _leave(interaction)
