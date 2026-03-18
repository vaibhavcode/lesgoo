import discord
from discord import app_commands
from utils.music import search, get_queue, play_next
from utils.errors import safe_send, user_not_in_voice
from utils.logger import get_logger

logger = get_logger("slash.play")


def _is_playlist(query: str) -> bool:
    return query.startswith("http") and ("list=" in query or "/playlist" in query)


async def _play(interaction: discord.Interaction, query: str):
    if interaction.user.voice is None:
        await user_not_in_voice(interaction)
        return
    vc = interaction.guild.voice_client
    if vc is None or not vc.is_connected():
        vc = await interaction.user.voice.channel.connect()
    elif vc.channel != interaction.user.voice.channel:
        await vc.move_to(interaction.user.voice.channel)
    await interaction.response.defer()
    is_playlist = _is_playlist(query)
    tracks = await search(query, interaction.user)
    if not tracks:
        await safe_send(interaction, "Couldn't find anything for that. Try a different search.")
        return
    mq = get_queue(interaction.guild.id)
    was_empty = mq.current is None and len(mq.queue) == 0
    if is_playlist:
        mq.add_many(tracks)
        msg = f"Playing playlist — **{len(tracks)} tracks** added to queue." if was_empty else f"Added **{len(tracks)} tracks** to the queue."
        await interaction.followup.send(msg)
    else:
        track = tracks[0]
        mq.add(track)
        msg = f"Playing **{track.title}** `{track.duration_str}`" if was_empty else f"Added to queue: **{track.title}** `{track.duration_str}`"
        await interaction.followup.send(msg)
    if was_empty:
        await play_next(interaction.guild)


def setup(bot, guild):
    @bot.tree.command(name="play", description="Play a song or playlist from YouTube", guild=guild)
    @app_commands.describe(query="Song name or YouTube URL")
    async def slash_play(interaction: discord.Interaction, query: str):
        await _play(interaction, query)
