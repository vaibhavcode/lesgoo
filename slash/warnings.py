import discord
from discord import app_commands
from utils.roles import is_mod
from utils.warnings import get_warnings, clear_warnings
from utils.errors import safe_send


class WarningsView(discord.ui.View):
    def __init__(self, guild: discord.Guild, user: discord.Member, invoker: discord.Member):
        super().__init__(timeout=60)
        self.guild = guild
        self.user = user
        self.invoker = invoker

    def build_embed(self) -> discord.Embed:
        records = get_warnings(self.guild.id, self.user.id)
        embed = discord.Embed(
            title=f"Warnings — {self.user.display_name}",
            color=discord.Color.yellow()
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        if not records:
            embed.description = "No warnings on record."
            self.clear_button.disabled = True
        else:
            for i, w in enumerate(records, 1):
                embed.add_field(
                    name=f"Warning #{i} — {w['timestamp'][:10]}",
                    value=f"**Reason:** {w['reason']}\n**Mod:** {w['mod']}",
                    inline=False
                )
            embed.set_footer(text=f"{len(records)} warning(s) total")
        return embed

    @discord.ui.button(label="Clear all warnings", style=discord.ButtonStyle.danger)
    async def clear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_mod(interaction.user):
            await interaction.response.send_message(
                "You don't have permission to clear warnings.", ephemeral=True
            )
            return
        clear_warnings(self.guild.id, self.user.id)
        button.disabled = True
        button.label = "Cleared"
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


async def _warnings(interaction: discord.Interaction, user: discord.Member):
    if not is_mod(interaction.user):
        await safe_send(interaction, "You don't have permission to view warnings.", ephemeral=True)
        return

    view = WarningsView(interaction.guild, user, interaction.user)
    embed = view.build_embed()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="warnings", description="View warnings for a user", guild=guild)
    @app_commands.describe(user="User to check warnings for")
    async def slash_warnings(interaction: discord.Interaction, user: discord.Member):
        await _warnings(interaction, user)
