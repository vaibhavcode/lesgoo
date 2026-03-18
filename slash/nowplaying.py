import discord
from utils.music import get_queue
from utils.errors import safe_send


class NowPlayingView(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=60)
        self.guild = guild
        self._update_buttons()

    def _update_buttons(self):
        vc = self.guild.voice_client
        is_playing = vc and (vc.is_playing() or vc.is_paused())
        is_paused = vc and vc.is_paused()
        self.pause_button.label = "Resume" if is_paused else "Pause"
        self.pause_button.disabled = not is_playing
        self.skip_button.disabled = not is_playing
        self.stop_button.disabled = not is_playing
        mq = get_queue(self.guild.id)
        self.loop_button.style = discord.ButtonStyle.success if mq.loop else discord.ButtonStyle.secondary

    def build_embed(self) -> discord.Embed:
        mq = get_queue(self.guild.id)
        track = mq.current

        if not track:
            return discord.Embed(description="Nothing is playing.", color=discord.Color.blurple())

        embed = discord.Embed(
            title="Now Playing",
            description=f"**[{track.title}]({track.webpage_url})**",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Duration", value=track.duration_str, inline=True)
        embed.add_field(name="Requested by", value=track.requester.mention, inline=True)
        embed.add_field(name="Loop", value="ON" if mq.loop else "OFF", inline=True)
        embed.add_field(name="Volume", value=f"{int(mq.volume * 100)}%", inline=True)
        embed.add_field(name="Queue", value=f"{len(mq.queue)} track(s) remaining", inline=True)

        if track.thumbnail:
            embed.set_thumbnail(url=track.thumbnail)

        return embed

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.primary, row=0)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.channel.send("Resumed.")
        elif vc and vc.is_playing():
            vc.pause()
            await interaction.channel.send("Paused.")
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, row=0)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.guild.voice_client
        mq = get_queue(self.guild.id)
        mq.loop = False
        mq.current = None
        if vc:
            vc.stop()
        await interaction.channel.send("Skipped.")
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, row=0)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.guild.voice_client
        mq = get_queue(self.guild.id)
        mq.clear()
        mq.loop = False
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
        await interaction.channel.send("Stopped playback and cleared the queue.")
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Loop", style=discord.ButtonStyle.secondary, row=0)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        mq = get_queue(self.guild.id)
        mq.loop = not mq.loop
        state = "ON" if mq.loop else "OFF"
        await interaction.channel.send(f"Loop is now **{state}**.")
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


async def _nowplaying(interaction: discord.Interaction):
    mq = get_queue(interaction.guild.id)

    if mq.current is None:
        await safe_send(interaction, "Nothing is playing right now.")
        return

    view = NowPlayingView(interaction.guild)
    embed = view.build_embed()
    await interaction.response.send_message(embed=embed, view=view)


def setup(bot, guild):
    @bot.tree.command(name="nowplaying", description="Show the currently playing track", guild=guild)
    async def slash_nowplaying(interaction: discord.Interaction):
        await _nowplaying(interaction)
