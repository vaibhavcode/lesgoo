import discord
import asyncio
from groq import Groq
from utils.memory import get_user_memory
from utils.config import config
from discord import app_commands

groq_client = Groq(api_key=config["GROQ_API_KEY"])


async def _beef(interaction: discord.Interaction, user: discord.Member):
    if user == interaction.client.user:
        await interaction.response.send_message("Start beef with *myself*? I am the standard.", ephemeral=True)
        return
    await interaction.response.defer()
    user_mem = get_user_memory(user.id)
    notes = "\n".join(user_mem["persona_notes"]) or "No prior knowledge."
    def _call():
        return groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=120,
            messages=[
                {"role": "system", "content": "You are Aarshi Lodia. Publicly call someone out dramatically. 2-3 sentences. No asterisks."},
                {"role": "user", "content": f"Call out {user.display_name}.\nKnown traits:\n{notes}"}
            ]
        )
    try:
        completion = await asyncio.to_thread(_call)
        callout = completion.choices[0].message.content.strip()
    except Exception:
        callout = "I have so much to say but this server's wifi is beneath me."
    await interaction.followup.send(
        f"Attention everyone. {interaction.user.display_name} has asked me to address **{user.mention}**.\n\n{callout}"
    )


def setup(bot, guild):
    @bot.tree.command(name="beef", description="Have Aarshi publicly call someone out", guild=guild)
    @app_commands.describe(user="The user to call out")
    async def slash_beef(interaction: discord.Interaction, user: discord.Member):
        await _beef(interaction, user)
