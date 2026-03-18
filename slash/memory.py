import discord
from utils.memory import get_user_memory, clear_user_memory
from utils.errors import safe_send


class MemoryView(discord.ui.View):
    def __init__(self, user: discord.Member):
        super().__init__(timeout=60)
        self.user = user

    def build_embed(self) -> discord.Embed:
        user_mem = get_user_memory(self.user.id)
        notes = user_mem["persona_notes"]
        history = user_mem["history"]

        embed = discord.Embed(
            title=f"Memory — {self.user.display_name}",
            description="Don't flatter yourself. I remember everything.",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.add_field(
            name="Persona notes",
            value="\n".join(notes) if notes else "Nothing yet.",
            inline=False
        )
        embed.add_field(
            name="Recent history (last 6 lines)",
            value=f"```{chr(10).join(history[-6:])}```" if history else "Nothing yet.",
            inline=False
        )
        return embed

    @discord.ui.button(label="Clear my memory", style=discord.ButtonStyle.danger)
    async def clear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You can only clear your own memory.", ephemeral=True
            )
            return
        clear_user_memory(self.user.id)
        button.disabled = True
        button.label = "Cleared"
        embed = self.build_embed()
        embed.description = "Memory wiped. Aarshi has no idea who you are anymore."
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


async def _memory(interaction: discord.Interaction):
    view = MemoryView(interaction.user)
    embed = view.build_embed()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="memory", description="See what Aarshi knows about you", guild=guild)
    async def slash_memory(interaction: discord.Interaction):
        await _memory(interaction)
