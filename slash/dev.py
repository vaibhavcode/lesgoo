import discord
import asyncio
import os
import json
from discord import app_commands
from utils.config import config
from utils.memory import get_all_memory, clear_user_memory, save_memory
from utils.roles import is_dev

DEV_ID = config["DEV_ID"]


def _dev_only(interaction: discord.Interaction) -> bool:
    return interaction.user.id == DEV_ID


# ---- Dev status panel ----

class DevStatusView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot

    def build_embed(self) -> discord.Embed:
        guilds = self.bot.guilds
        vc_count = sum(1 for g in guilds if g.voice_client and g.voice_client.is_connected())
        all_mem = get_all_memory()
        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(title="Dev Status", color=discord.Color.blurple())
        embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="Guilds", value=str(len(guilds)), inline=True)
        embed.add_field(name="Voice connections", value=str(vc_count), inline=True)
        embed.add_field(name="Users in memory", value=str(len(all_mem)), inline=True)
        embed.add_field(
            name="Total messages",
            value=str(sum(
                len([h for h in v["history"] if h.startswith("User:")])
                for v in all_mem.values()
            )),
            inline=True
        )
        guild_list = "\n".join(f"• {g.name} (`{g.id}`)" for g in guilds)
        embed.add_field(name="Guild list", value=guild_list or "None", inline=False)
        return embed

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


# ---- Dev clear all confirmation ----

class DevClearAllView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Confirm — wipe all memory", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not _dev_only(interaction):
            await interaction.response.send_message("You're not the developer.", ephemeral=True)
            return
        all_mem = get_all_memory()
        count = len(all_mem)
        for user_id in list(all_mem.keys()):
            all_mem[user_id] = {"history": [], "persona_notes": []}
        save_memory()
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content=f"All memory wiped — {count} user(s) cleared.",
            embed=None,
            view=self
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="Cancelled.", embed=None, view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


# ---- Handlers ----

async def _devping(interaction: discord.Interaction):
    if not _dev_only(interaction):
        await interaction.response.send_message("You're not the developer.", ephemeral=True)
        return
    latency = round(interaction.client.latency * 1000)
    await interaction.response.send_message(f"Dev ping — **{latency}ms**.", ephemeral=True)


async def _devmemory(interaction: discord.Interaction, user: discord.Member = None):
    if not _dev_only(interaction):
        await interaction.response.send_message("You're not the developer.", ephemeral=True)
        return
    if user:
        from utils.memory import get_user_memory
        mem = get_user_memory(user.id)
        text = json.dumps(mem, indent=2)
        if len(text) > 1900:
            text = text[:1900] + "\n... (truncated)"
        await interaction.response.send_message(f"```json\n{text}\n```", ephemeral=True)
    else:
        all_mem = get_all_memory()
        total_users = len(all_mem)
        total_messages = sum(
            len([h for h in v["history"] if h.startswith("User:")])
            for v in all_mem.values()
        )
        await interaction.response.send_message(
            f"**Memory stats**\nTotal users: `{total_users}`\nTotal messages: `{total_messages}`",
            ephemeral=True
        )


async def _devclearall(interaction: discord.Interaction):
    if not _dev_only(interaction):
        await interaction.response.send_message("You're not the developer.", ephemeral=True)
        return
    all_mem = get_all_memory()
    embed = discord.Embed(
        title="Confirm — wipe all memory",
        description=f"This will clear memory for **{len(all_mem)} user(s)**. This cannot be undone.",
        color=discord.Color.red()
    )
    view = DevClearAllView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def _devstatus(interaction: discord.Interaction):
    if not _dev_only(interaction):
        await interaction.response.send_message("You're not the developer.", ephemeral=True)
        return
    view = DevStatusView(interaction.client)
    embed = view.build_embed()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def _devsetallowedchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not _dev_only(interaction):
        await interaction.response.send_message("You're not the developer.", ephemeral=True)
        return
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    with open(config_path, "r") as f:
        data = json.load(f)
    data["ALLOWED_TEXT_CHANNEL_ID"] = channel.id
    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)
    config["ALLOWED_TEXT_CHANNEL_ID"] = channel.id
    await interaction.response.send_message(
        f"Allowed channel updated to **#{channel.name}**.", ephemeral=True
    )


async def _devannounce(interaction: discord.Interaction, message: str):
    if not _dev_only(interaction):
        await interaction.response.send_message("You're not the developer.", ephemeral=True)
        return
    allowed_channel = interaction.guild.get_channel(config["ALLOWED_TEXT_CHANNEL_ID"])
    if allowed_channel is None:
        await interaction.response.send_message("Allowed channel not found.", ephemeral=True)
        return
    await allowed_channel.send(message)
    await interaction.response.send_message("Announced.", ephemeral=True)


# ---- Setup ----

def setup(bot, guild):

    @bot.tree.command(name="devping", description="[DEV] Check bot latency", guild=guild)
    async def slash_devping(interaction: discord.Interaction):
        await _devping(interaction)

    @bot.tree.command(name="devmemory", description="[DEV] Inspect memory", guild=guild)
    @app_commands.describe(user="User to inspect (leave blank for global stats)")
    async def slash_devmemory(interaction: discord.Interaction, user: discord.Member = None):
        await _devmemory(interaction, user)

    @bot.tree.command(name="devclearall", description="[DEV] Wipe all memory for all users", guild=guild)
    async def slash_devclearall(interaction: discord.Interaction):
        await _devclearall(interaction)

    @bot.tree.command(name="devstatus", description="[DEV] Full bot status", guild=guild)
    async def slash_devstatus(interaction: discord.Interaction):
        await _devstatus(interaction)

    @bot.tree.command(name="devsetallowedchannel", description="[DEV] Change the allowed text channel", guild=guild)
    @app_commands.describe(channel="Channel to set as the allowed text channel")
    async def slash_devsetallowedchannel(interaction: discord.Interaction, channel: discord.TextChannel):
        await _devsetallowedchannel(interaction, channel)

    @bot.tree.command(name="devannounce", description="[DEV] Send a message to the allowed channel", guild=guild)
    @app_commands.describe(message="Message to announce")
    async def slash_devannounce(interaction: discord.Interaction, message: str):
        await _devannounce(interaction, message)
