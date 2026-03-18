import discord
from utils.music import get_queue
from utils.errors import safe_send


async def _shuffle(interaction: discord.Interaction):
    mq = get_queue(interaction.guild.id)

    if not mq.queue:
        await safe_send(interaction, "The queue is empty — nothing to shuffle.", ephemeral=True)
        return

    mq.shuffle()
    await safe_send(interaction, f"Shuffled **{len(mq.queue)} tracks** in the queue.")


def setup(bot, guild):
    @bot.tree.command(name="shuffle", description="Shuffle the music queue", guild=guild)
    async def slash_shuffle(interaction: discord.Interaction):
        await _shuffle(interaction)
