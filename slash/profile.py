import discord
import asyncio
from groq import Groq
from utils.memory import get_user_memory
from utils.config import config
from discord import app_commands

groq_client = Groq(api_key=config["GROQ_API_KEY"])


async def _profile(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer()
    user_mem = get_user_memory(user.id)
    notes = "\n".join(user_mem["persona_notes"]) or "No notes yet."
    history = "\n".join(user_mem["history"][-6:]) or "No history."
    message_count = len([h for h in user_mem["history"] if h.startswith("User:")])
    def _call():
        return groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=100,
            messages=[
                {"role": "system", "content": "You are Aarshi Lodia. Give your honest opinion of this person in 2 sentences. Be dramatic. No asterisks."},
                {"role": "user", "content": f"Opinion of {user.display_name}.\nTraits:\n{notes}\nMessages:\n{history}"}
            ]
        )
    try:
        completion = await asyncio.to_thread(_call)
        opinion = completion.choices[0].message.content.strip()
    except Exception:
        opinion = "I don't have enough data. Which is probably for the best."
    embed = discord.Embed(title=f"Aarshi's profile of {user.display_name}", color=discord.Color.blurple())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Opinion", value=opinion, inline=False)
    embed.add_field(name="Known traits", value=notes, inline=False)
    embed.add_field(name="Messages sent", value=str(message_count), inline=True)
    await interaction.followup.send(embed=embed)


def setup(bot, guild):
    @bot.tree.command(name="profile", description="Get Aarshi's opinion of a user", guild=guild)
    @app_commands.describe(user="The user to profile")
    async def slash_profile(interaction: discord.Interaction, user: discord.Member):
        await _profile(interaction, user)
