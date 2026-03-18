import discord
from discord import app_commands
from utils.roles import is_mod
from utils.errors import safe_send


class BanConfirmView(discord.ui.View):
    def __init__(self, user: discord.Member, reason: str):
        super().__init__(timeout=60)
        self.user = user
        self.reason = reason

    @discord.ui.button(label="Confirm Ban", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.user.ban(reason=self.reason, delete_message_days=0)
            for item in self.children:
                item.disabled = True
            embed = discord.Embed(title="User banned", color=discord.Color.dark_red())
            embed.add_field(name="User", value=self.user.name, inline=True)
            embed.add_field(name="Reason", value=self.reason, inline=False)
            embed.add_field(name="Mod", value=interaction.user.mention, inline=True)
            await interaction.response.edit_message(embed=embed, view=self)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to ban that user.", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="Ban cancelled.", embed=None, view=self
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


async def _ban(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not is_mod(interaction.user):
        await safe_send(interaction, "You don't have permission to ban users.", ephemeral=True)
        return
    if user == interaction.client.user:
        await safe_send(interaction, "Ban *me*? You wouldn't dare.", ephemeral=True)
        return
    if user.guild_permissions.administrator:
        await safe_send(interaction, "I can't ban an administrator.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Confirm Ban",
        description=f"Are you sure you want to ban **{user.display_name}**?",
        color=discord.Color.red()
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_thumbnail(url=user.display_avatar.url)

    view = BanConfirmView(user, reason)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="ban", description="Ban a user from the server", guild=guild)
    @app_commands.describe(user="User to ban", reason="Reason for the ban")
    async def slash_ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await _ban(interaction, user, reason)
