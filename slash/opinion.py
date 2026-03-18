import discord
import asyncio
from discord import app_commands
from groq import Groq
from utils.config import config
from utils.errors import safe_send

groq_client = Groq(api_key=config["GROQ_API_KEY"])


async def _opinion(interaction: discord.Interaction, topic: str):
    await interaction.response.defer()

    def _call():
        return groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=100,
            messages=[
                {"role": "system", "content": "You are Aarshi Lodia. Give a hot take in 2 sentences. Make it about yourself where possible. No asterisks."},
                {"role": "user", "content": f"Give your opinion on: {topic}"}
            ]
        )

    try:
        completion = await asyncio.to_thread(_call)
        response = completion.choices[0].message.content.strip()
    except Exception:
        response = "I have opinions but this server can't handle them right now."
    await interaction.followup.send(f"**On {topic}:** {response}")


def setup(bot, guild):
    @bot.tree.command(name="opinion", description="Get Aarshi's hot take on any topic", guild=guild)
    @app_commands.describe(topic="Topic to get an opinion on")
    async def slash_opinion(interaction: discord.Interaction, topic: str):
        await _opinion(interaction, topic)
