import discord
import asyncio
from groq import Groq
from utils.memory import get_user_memory
from utils.config import config
from discord import app_commands

groq_client = Groq(api_key=config["GROQ_API_KEY"])


async def _roast(interaction: discord.Interaction, user: discord.Member):
    if user == interaction.client.user:
        await interaction.response.send_message("Roast *myself*? I am flawless.", ephemeral=True)
        return
    await interaction.response.defer()
    user_mem = get_user_memory(user.id)
    notes = "\n".join(user_mem["persona_notes"]) or "No notes."
    history = "\n".join(user_mem["history"][-6:]) or "No history."
    def _call():
        return groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=120,
            messages=[
                {"role": "system", "content": "You are Aarshi Lodia. Roast the user in 2-3 sentences using their traits. Be savage but witty. No asterisks."},
                {"role": "user", "content": f"Roast {user.display_name}.\nTraits:\n{notes}\nMessages:\n{history}"}
            ]
        )
    try:
        completion = await asyncio.to_thread(_call)
        response = completion.choices[0].message.content.strip()
    except Exception:
        response = "Something broke. Even my roasts are too powerful."
    await interaction.followup.send(f"**{user.display_name}**, {response}")


def setup(bot, guild):
    @bot.tree.command(name="roast", description="Have Aarshi roast someone", guild=guild)
    @app_commands.describe(user="The user to roast")
    async def slash_roast(interaction: discord.Interaction, user: discord.Member):
        await _roast(interaction, user)
