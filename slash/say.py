import discord
import asyncio
import os
import time
from discord import app_commands
from elevenlabs.client import ElevenLabs
from utils.config import config

eleven = ElevenLabs(api_key=config["ELEVENLABS_API_KEY"])


async def _say(interaction: discord.Interaction, text: str):
    vc = interaction.guild.voice_client
    if vc is None or not vc.is_connected():
        await interaction.response.send_message("I'm not in a voice channel. Use `/join` first.", ephemeral=True)
        return
    await interaction.response.send_message(f"Saying: *{text}*")
    def _generate():
        return eleven.text_to_speech.convert(
            voice_id=config["VOICE_ID"],
            model_id="eleven_multilingual_v2",
            text=text
        )
    try:
        if vc.is_playing():
            vc.stop()
        audio = await asyncio.to_thread(_generate)
        filename = f"tts_{int(time.time() * 1000)}.mp3"
        with open(filename, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        vc.play(discord.FFmpegPCMAudio(filename))
        while vc.is_playing():
            await asyncio.sleep(0.5)
        try:
            os.remove(filename)
        except OSError:
            pass
    except Exception as e:
        print("say error:", e)


def setup(bot, guild):
    @bot.tree.command(name="say", description="Make Aarshi say something in voice", guild=guild)
    @app_commands.describe(text="What Aarshi should say")
    async def slash_say(interaction: discord.Interaction, text: str):
        await _say(interaction, text)
