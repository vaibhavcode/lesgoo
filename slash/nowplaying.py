import discord
from utils.music import get_queue
from utils.errors import safe_send


async def _nowplaying(interaction: discord.Interaction):
    mq = get_queue(interaction.guild.id)

    if mq.current is None:
        await safe_send(interaction, "Nothing is playing right now.", ephemeral=True)
        return

    track = mq.current
    embed = discord.Embed(
        title="Now Playing",
        description=f"**[{track.title}]({track.webpage_url})**",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Duration", value=track.duration_str, inline=True)
    embed.add_field(name="Requested by", value=track.requester.mention, inline=True)
    embed.add_field(name="Loop", value="ON" if mq.loop else "OFF", inline=True)
    embed.add_field(name="Volume", value=f"{int(mq.volume * 100)}%", inline=True)

    if track.thumbnail:
        embed.set_thumbnail(url=track.thumbnail)

    await safe_send(interaction, embed=embed)


def setup(bot, guild):
    @bot.tree.command(name="nowplaying", description="Show the currently playing track", guild=guild)
    async def slash_nowplaying(interaction: discord.Interaction):
        await _nowplaying(interaction)
