import discord
from utils.music import get_queue
from utils.errors import safe_send


async def _queue(interaction: discord.Interaction):
    mq = get_queue(interaction.guild.id)

    if mq.current is None and not mq.queue:
        await safe_send(interaction, "The queue is empty.", ephemeral=True)
        return

    embed = discord.Embed(title="Music Queue", color=discord.Color.blurple())

    if mq.current:
        embed.add_field(
            name="Now playing",
            value=f"**{mq.current.title}** `{mq.current.duration_str}` — requested by {mq.current.requester.mention}",
            inline=False
        )
        if mq.current.thumbnail:
            embed.set_thumbnail(url=mq.current.thumbnail)

    if mq.queue:
        queue_text = "\n".join(
            f"`{i+1}.` **{t.title}** `{t.duration_str}` — {t.requester.mention}"
            for i, t in enumerate(mq.queue[:10])
        )
        if len(mq.queue) > 10:
            queue_text += f"\n*...and {len(mq.queue) - 10} more*"
        embed.add_field(name=f"Up next ({len(mq.queue)} track(s))", value=queue_text, inline=False)

    total_duration = sum(t.duration for t in mq.queue if t.duration)
    m, s = divmod(total_duration, 60)
    h, m = divmod(m, 60)
    duration_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"

    footer_parts = [f"Total queue time: {duration_str}"]
    if mq.loop:
        footer_parts.append("Loop: ON")
    embed.set_footer(text=" · ".join(footer_parts))

    await safe_send(interaction, embed=embed)


def setup(bot, guild):
    @bot.tree.command(name="queue", description="Show the current music queue", guild=guild)
    async def slash_queue(interaction: discord.Interaction):
        await _queue(interaction)
