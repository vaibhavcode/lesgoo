import discord
from discord import app_commands
from utils.roles import is_mod
from utils.errors import safe_send


class KickConfirmView(discord.ui.View):
    def __init__(self, user: discord.Member, reason: str):
        super().__init__(timeout=60)
        self.user = user
        self.reason = reason

    @discord.ui.button(label="Confirm Kick", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.user.kick(reason=self.reason)
            for item in self.children:
                item.disabled = True
            embed = discord.Embed(title="User kicked", color=discord.Color.red())
            embed.add_field(name="User", value=self.user.name, inline=True)
            embed.add_field(name="Reason", value=self.reason, inline=False)
            embed.add_field(name="Mod", value=interaction.user.mention, inline=True)
            await interaction.response.edit_message(embed=embed, view=self)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to kick that user.", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="Kick cancelled.", embed=None, view=self
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


async def _kick(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not is_mod(interaction.user):
        await safe_send(interaction, "You don't have permission to kick users.", ephemeral=True)
        return
    if user == interaction.client.user:
        await safe_send(interaction, "Kick *me*? Absolutely not.", ephemeral=True)
        return
    if user.guild_permissions.administrator:
        await safe_send(interaction, "I can't kick an administrator.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Confirm Kick",
        description=f"Are you sure you want to kick **{user.display_name}**?",
        color=discord.Color.orange()
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_thumbnail(url=user.display_avatar.url)

    view = KickConfirmView(user, reason)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="kick", description="Kick a user from the server", guild=guild)
    @app_commands.describe(user="User to kick", reason="Reason for the kick")
    async def slash_kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await _kick(interaction, user, reason)
