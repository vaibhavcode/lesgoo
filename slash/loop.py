import discord
from utils.music import get_queue
from utils.errors import safe_send


async def _loop(interaction: discord.Interaction):
    mq = get_queue(interaction.guild.id)

    if mq.current is None:
        await safe_send(interaction, "Nothing is playing to loop.", ephemeral=True)
        return

    mq.loop = not mq.loop
    state = "ON" if mq.loop else "OFF"
    await safe_send(interaction, f"Loop is now **{state}**.")


def setup(bot, guild):
    @bot.tree.command(name="loop", description="Toggle looping the current track", guild=guild)
    async def slash_loop(interaction: discord.Interaction):
        await _loop(interaction)
