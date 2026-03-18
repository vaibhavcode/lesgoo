import asyncio
import importlib
import os
import traceback
import discord
from discord import app_commands
from discord.ext import commands

from utils.config import config
from utils.ai import ask_ai
from utils.tts import speak
from utils.logger import bot_logger, slash_logger
from utils.errors import safe_send, unexpected_error
from utils.music import set_event_loop

GUILD = discord.Object(id=1287755847321260124)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ================= SLASH COMMAND LOADER =================

def load_slash_commands():
    slash_dir = os.path.join(os.path.dirname(__file__), "slash")
    loaded = 0
    failed = 0
    for filename in sorted(os.listdir(slash_dir)):
        if filename.startswith("_") or not filename.endswith(".py"):
            continue
        module_name = f"slash.{filename[:-3]}"
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "setup"):
                module.setup(bot, GUILD)
                slash_logger.info(f"Loaded slash: {module_name}")
                loaded += 1
            else:
                slash_logger.warning(f"Skipped slash: {module_name} (no setup function)")
        except Exception as e:
            slash_logger.error(f"Failed to load slash: {module_name} — {e}\n{traceback.format_exc()}")
            failed += 1
    bot_logger.info(f"Slash commands: {loaded} loaded, {failed} failed")


# ================= GLOBAL ERROR HANDLER =================

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    command_name = interaction.command.name if interaction.command else "unknown"

    if isinstance(error, app_commands.CommandNotFound):
        bot_logger.warning(f"Unknown command used: {command_name}")
        await safe_send(interaction, "I don't know that command.", ephemeral=True)

    elif isinstance(error, app_commands.MissingPermissions):
        bot_logger.warning(f"Missing permissions for {command_name} by {interaction.user}")
        await safe_send(interaction, "You don't have permission to use this command.", ephemeral=True)

    elif isinstance(error, app_commands.BotMissingPermissions):
        bot_logger.error(f"Bot missing permissions for {command_name}: {error.missing_permissions}")
        await safe_send(interaction, f"I'm missing permissions to do that: `{', '.join(error.missing_permissions)}`", ephemeral=True)

    elif isinstance(error, app_commands.CommandOnCooldown):
        await safe_send(interaction, f"Slow down. Try again in {error.retry_after:.1f}s.", ephemeral=True)

    elif isinstance(error, app_commands.CheckFailure):
        bot_logger.warning(f"Check failed for {command_name} by {interaction.user}")
        await safe_send(interaction, "You don't have permission to use this command.", ephemeral=True)

    else:
        tb = traceback.format_exc()
        bot_logger.error(f"Unhandled error in /{command_name} by {interaction.user}: {error}\n{tb}")
        await safe_send(
            interaction,
            "Something broke. It's *definitely* not my fault. Try again.",
            ephemeral=True
        )


# ================= EVENTS =================

@bot.event
async def on_ready():
    bot_logger.info(f"Bot online: {bot.user} (ID: {bot.user.id})")
    set_event_loop(asyncio.get_event_loop())
    try:
        synced = await bot.tree.sync(guild=GUILD)
        bot_logger.info(f"Synced {len(synced)} slash command(s): {[c.name for c in synced]}")
    except Exception as e:
        bot_logger.error(f"Failed to sync slash commands: {e}")


@bot.event
async def on_guild_join(guild: discord.Guild):
    bot_logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")


@bot.event
async def on_guild_remove(guild: discord.Guild):
    bot_logger.info(f"Removed from guild: {guild.name} (ID: {guild.id})")


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # Auto-disconnect if the bot is left alone in a voice channel
    vc = member.guild.voice_client
    if vc and vc.is_connected():
        if len(vc.channel.members) == 1:
            await vc.disconnect()
            bot_logger.info(f"Auto-disconnected from {vc.channel.name} in {member.guild.name} — no listeners")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    if message.channel.id != config["ALLOWED_TEXT_CHANNEL_ID"]:
        return

    if bot.user not in message.mentions:
        return

    question = message.content.replace(
        f"<@{bot.user.id}>", ""
    ).replace(
        f"<@!{bot.user.id}>", ""
    ).strip()

    if not question:
        await message.channel.send("What do you want?")
        return

    bot_logger.info(f"Mention from {message.author} ({message.author.id}): {question[:60]}")

    async with message.channel.typing():
        try:
            response = await ask_ai(
                message.author.id,
                message.author.name,
                question
            )
            await asyncio.sleep(1)
        except Exception as e:
            bot_logger.error(f"ask_ai failed for {message.author}: {e}\n{traceback.format_exc()}")
            await message.channel.send(
                "Ugh, I can't even right now. Something broke and it's *definitely* not my fault."
            )
            return

    await message.channel.send(response)

    vc = message.guild.voice_client
    if vc and message.author.voice:
        await speak(vc, response, message.author.id)


@bot.event
async def on_error(event: str, *args, **kwargs):
    bot_logger.error(f"Unhandled error in event '{event}':\n{traceback.format_exc()}")


# ================= RUN =================

async def main():
    async with bot:
        load_slash_commands()
        bot_logger.info("Starting bot...")
        try:
            await bot.start(config["DISCORD_TOKEN"])
        except discord.LoginFailure:
            bot_logger.critical("Invalid Discord token — check your config.json")
        except Exception as e:
            bot_logger.critical(f"Fatal error during bot startup: {e}\n{traceback.format_exc()}")


asyncio.run(main())
