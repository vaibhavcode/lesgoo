import asyncio
import os
import time
import discord
from elevenlabs.client import ElevenLabs
from utils.config import config
from utils.logger import tts_logger

eleven = ElevenLabs(api_key=config["ELEVENLABS_API_KEY"])

_tts_cache: dict[str, str] = {}
_tts_cache_order: list[str] = []
_voice_cooldown: dict[int, float] = {}

MAX_TTS_LENGTH = config["MAX_TTS_LENGTH"]
VOICE_COOLDOWN_SECONDS = config["VOICE_COOLDOWN_SECONDS"]
TTS_CACHE_MAX_SIZE = config["TTS_CACHE_MAX_SIZE"]


def _safe_sentence_limit(text: str, max_chars: int = MAX_TTS_LENGTH) -> str:
    if len(text) <= max_chars:
        return text
    sentences = text.split(".")
    output = ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if len(output) + len(s) + 1 < max_chars:
            output += s + ". "
        else:
            break
    return output.strip()


def _evict_cache_if_needed():
    while len(_tts_cache) >= TTS_CACHE_MAX_SIZE:
        oldest_key = _tts_cache_order.pop(0)
        filename = _tts_cache.pop(oldest_key, None)
        if filename:
            try:
                os.remove(filename)
                tts_logger.debug(f"Evicted TTS cache file: {filename}")
            except OSError as e:
                tts_logger.warning(f"Failed to delete cached TTS file {filename}: {e}")


async def speak(vc: discord.VoiceClient, text: str, user_id: int):
    if vc is None or not vc.is_connected():
        tts_logger.warning("speak() called but voice client is not connected")
        return

    if vc.channel is None:
        return

    if len(vc.channel.members) <= 1:
        tts_logger.debug("No listeners in voice channel — skipping TTS")
        return

    now = time.time()
    if user_id in _voice_cooldown:
        remaining = VOICE_COOLDOWN_SECONDS - (now - _voice_cooldown[user_id])
        if remaining > 0:
            tts_logger.debug(f"TTS cooldown active for user {user_id} — {remaining:.1f}s remaining")
            return

    _voice_cooldown[user_id] = now

    if vc.is_playing():
        vc.stop()

    tts_text = _safe_sentence_limit(text)

    try:
        if tts_text in _tts_cache:
            filename = _tts_cache[tts_text]
            tts_logger.debug(f"TTS cache hit for user {user_id}")
        else:
            _evict_cache_if_needed()

            def _generate():
                return eleven.text_to_speech.convert(
                    voice_id=config["VOICE_ID"],
                    model_id="eleven_multilingual_v2",
                    text=tts_text
                )

            audio = await asyncio.to_thread(_generate)
            filename = f"tts_{abs(hash(tts_text))}.mp3"

            with open(filename, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

            _tts_cache[tts_text] = filename
            _tts_cache_order.append(tts_text)
            tts_logger.info(f"Generated TTS for user {user_id}")

        vc.play(discord.FFmpegPCMAudio(filename))

        while vc.is_playing():
            await asyncio.sleep(0.5)

    except Exception as e:
        tts_logger.error(f"TTS error for user {user_id}: {e}")
