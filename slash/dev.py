import discord
import asyncio
import importlib
import os
import json
from discord import app_commands
from utils.config import config
from utils.memory import get_all_memory, clear_user_memory, save_memory
from utils.roles import is_dev

DEV_ID = config["DEV_ID"]


def _dev_only(interaction: discord.Interaction) -> bool:
    return interaction.user.id == DEV_ID


# ---- Dev commands ----

async def _devping(interaction: discord.Interaction):
    if not _dev_only(interaction):
        await interaction.response.send_message("You're not the developer.", ephemeral=True)
        return
    latency = round(interaction.client.latency * 1000)
    await interaction.response.send_message(
        f"Dev ping — **{latency}ms**. Bot is alive.", ephemeral=True
    )


async def _devreload(interaction: discord.Interaction, module: str):
    if not _dev_only(interaction):
        await interaction.response.send_message("You're not the developer.", ephemeral=True)
        return
    try:
        await interaction.client.reload_extension(module)
        await interaction.response.send_message(f"Reloaded `{module}`.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed: `{e}`", ephemeral=True)


async def _devmemory(interaction: discord.Interaction, user: discord.Member = None):
    if not _dev_only(interaction):
        await interaction.response.send_message("You're not the developer.", ephemeral=True)
        return

    if user:
        from utils.memory import get_user_memory
        mem = get_user_memory(user.id)
        text = json.dumps(mem, indent=2)
        # Split if too long for Discord
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
    for user_id in list(all_mem.keys()):
        all_mem[user_id] = {"history": [], "persona_notes": []}
    save_memory()

    await interaction.response.send_message(
        "All memory wiped across all users.", ephemeral=True
    )


async def _devstatus(interaction: discord.Interaction):
    if not _dev_only(interaction):
        await interaction.response.send_message("You're not the developer.", ephemeral=True)
        return

    guilds = interaction.client.guilds
    vc_count = sum(1 for g in guilds if g.voice_client and g.voice_client.is_connected())
    all_mem = get_all_memory()

    embed = discord.Embed(title="Dev Status", color=discord.Color.blurple())
    embed.add_field(name="Latency", value=f"{round(interaction.client.latency * 1000)}ms", inline=True)
    embed.add_field(name="Guilds", value=str(len(guilds)), inline=True)
    embed.add_field(name="Voice connections", value=str(vc_count), inline=True)
    embed.add_field(name="Users in memory", value=str(len(all_mem)), inline=True)
    embed.add_field(
        name="Total messages stored",
        value=str(sum(
            len([h for h in v["history"] if h.startswith("User:")])
            for v in all_mem.values()
        )),
        inline=True
    )

    guild_list = "\n".join(f"• {g.name} (`{g.id}`)" for g in guilds)
    embed.add_field(name="Guild list", value=guild_list or "None", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


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
        f"Allowed text channel updated to **#{channel.name}**. Takes effect immediately.",
        ephemeral=True
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

    @bot.tree.command(name="devreload", description="[DEV] Reload a module", guild=guild)
    @app_commands.describe(module="Module to reload e.g. cogs.join")
    async def slash_devreload(interaction: discord.Interaction, module: str):
        await _devreload(interaction, module)

    @bot.tree.command(name="devmemory", description="[DEV] Inspect memory for a user or all users", guild=guild)
    @app_commands.describe(user="User to inspect (leave blank for global stats)")
    async def slash_devmemory(interaction: discord.Interaction, user: discord.Member = None):
        await _devmemory(interaction, user)

    @bot.tree.command(name="devclearall", description="[DEV] Wipe all memory for all users", guild=guild)
    async def slash_devclearall(interaction: discord.Interaction):
        await _devclearall(interaction)

    @bot.tree.command(name="devstatus", description="[DEV] Full bot status across all guilds", guild=guild)
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
