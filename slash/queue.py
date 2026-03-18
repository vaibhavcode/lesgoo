import discord
from discord import app_commands
from utils.music import get_queue, play_next
from utils.errors import safe_send
from utils.logger import get_logger

logger = get_logger("slash.queue")

TRACKS_PER_PAGE = 10


class QueueView(discord.ui.View):
    def __init__(self, guild: discord.Guild, page: int = 0):
        super().__init__(timeout=60)
        self.guild = guild
        self.page = page
        self._update_buttons()

    def _update_buttons(self):
        mq = get_queue(self.guild.id)
        total_pages = max(1, -(-len(mq.queue) // TRACKS_PER_PAGE))
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page >= total_pages - 1
        vc = self.guild.voice_client
        is_playing = vc and (vc.is_playing() or vc.is_paused())
        is_paused = vc and vc.is_paused()
        self.pause_button.label = "Resume" if is_paused else "Pause"
        self.pause_button.disabled = not is_playing
        self.skip_button.disabled = not is_playing
        self.stop_button.disabled = not is_playing
        self.loop_button.style = discord.ButtonStyle.success if get_queue(self.guild.id).loop else discord.ButtonStyle.secondary

    def build_embed(self) -> discord.Embed:
        mq = get_queue(self.guild.id)
        total_pages = max(1, -(-len(mq.queue) // TRACKS_PER_PAGE))

        container = discord.Embed(color=discord.Color.blurple())

        if mq.current:
            container.add_field(
                name="Now playing",
                value=f"**{mq.current.title}** `{mq.current.duration_str}`\nRequested by {mq.current.requester.mention}",
                inline=False
            )

        if mq.queue:
            start = self.page * TRACKS_PER_PAGE
            end = start + TRACKS_PER_PAGE
            tracks = mq.queue[start:end]
            queue_text = "\n".join(
                f"`{start + i + 1}.` **{t.title}** `{t.duration_str}` — {t.requester.mention}"
                for i, t in enumerate(tracks)
            )
            container.add_field(
                name=f"Up next — page {self.page + 1}/{total_pages} ({len(mq.queue)} track(s))",
                value=queue_text,
                inline=False
            )

            total_duration = sum(t.duration for t in mq.queue if t.duration)
            m, s = divmod(int(total_duration), 60)
            h, m = divmod(m, 60)
            duration_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
            footer = f"Total queue time: {duration_str}"
            if mq.loop:
                footer += " · Loop: ON"
            container.set_footer(text=footer)
        else:
            container.add_field(name="Queue", value="Nothing else in the queue.", inline=False)

        return container

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary, row=1)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary, row=1)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

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

    @discord.ui.button(label="Shuffle", style=discord.ButtonStyle.secondary, row=1)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        mq = get_queue(self.guild.id)
        if not mq.queue:
            await interaction.response.send_message("Nothing to shuffle.", ephemeral=True)
            return
        mq.shuffle()
        await interaction.channel.send(f"Shuffled **{len(mq.queue)} tracks**.")
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


async def _queue(interaction: discord.Interaction):
    mq = get_queue(interaction.guild.id)

    if mq.current is None and not mq.queue:
        await safe_send(interaction, "The queue is empty.")
        return

    view = QueueView(interaction.guild)
    embed = view.build_embed()
    await interaction.response.send_message(embed=embed, view=view)


def setup(bot, guild):
    @bot.tree.command(name="queue", description="Show the music queue", guild=guild)
    async def slash_queue(interaction: discord.Interaction):
        await _queue(interaction)
