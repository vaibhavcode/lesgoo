import discord
import random
from utils.errors import safe_send

_mood: dict[int, str] = {}
MOODS = ["annoyed", "dramatic", "suspicious", "flattered", "bored", "outraged"]
DESCRIPTIONS = {
    "annoyed": "Everyone is bothering me today. As usual.",
    "dramatic": "Everything is a crisis and nobody understands.",
    "suspicious": "I don't trust anyone in this server right now.",
    "flattered": "Someone said something nice. I'm choosing to believe it was about me.",
    "bored": "This server is painfully uninteresting today.",
    "outraged": "I cannot believe what has been said to me today. Unacceptable."
}


def get_mood(guild_id: int) -> str:
    if guild_id not in _mood:
        _mood[guild_id] = random.choice(MOODS)
    return _mood[guild_id]


async def _mood(interaction: discord.Interaction):
    current = get_mood(interaction.guild.id)
    await safe_send(interaction, f"I'm feeling **{current}**. {DESCRIPTIONS[current]}")


def setup(bot, guild):
    @bot.tree.command(name="mood", description="Check Aarshi's current mood", guild=guild)
    async def slash_mood(interaction: discord.Interaction):
        await _mood(interaction)
