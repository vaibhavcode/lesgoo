import discord
import asyncio
from discord import app_commands
from groq import Groq
from utils.memory import get_user_memory
from utils.config import config
from utils.errors import safe_send

groq_client = Groq(api_key=config["GROQ_API_KEY"])


class ProfileView(discord.ui.View):
    def __init__(self, guild: discord.Guild, user: discord.Member, opinion: str):
        super().__init__(timeout=60)
        self.guild = guild
        self.user = user
        self.opinion = opinion

    def build_embed(self) -> discord.Embed:
        user_mem = get_user_memory(self.user.id)
        notes = "\n".join(user_mem["persona_notes"]) if user_mem["persona_notes"] else "No notes yet."
        message_count = len([h for h in user_mem["history"] if h.startswith("User:")])

        embed = discord.Embed(
            title=f"Profile — {self.user.display_name}",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.add_field(name="Aarshi's opinion", value=self.opinion, inline=False)
        embed.add_field(name="Known traits", value=notes, inline=False)
        embed.add_field(name="Messages sent", value=str(message_count), inline=True)
        return embed

    @discord.ui.button(label="Roast", style=discord.ButtonStyle.danger)
    async def roast_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_mem = get_user_memory(self.user.id)
        notes = "\n".join(user_mem["persona_notes"]) or "No notes."
        history = "\n".join(user_mem["history"][-6:]) or "No history."

        def _call():
            return groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile", max_tokens=120,
                messages=[
                    {"role": "system", "content": "You are Aarshi Lodia. Roast the user in 2-3 sentences using their traits. Be savage but witty. No asterisks."},
                    {"role": "user", "content": f"Roast {self.user.display_name}.\nTraits:\n{notes}\nMessages:\n{history}"}
                ]
            )

        try:
            completion = await asyncio.to_thread(_call)
            response = completion.choices[0].message.content.strip()
        except Exception:
            response = "Something broke. Even my roasts are too powerful."

        await interaction.followup.send(f"**{self.user.display_name}**, {response}")

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


async def _profile(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer()

    user_mem = get_user_memory(user.id)
    notes = "\n".join(user_mem["persona_notes"]) or "No notes yet."
    history = "\n".join(user_mem["history"][-6:]) or "No history."

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

    view = ProfileView(interaction.guild, user, opinion)
    embed = view.build_embed()
    await interaction.followup.send(embed=embed, view=view)


def setup(bot, guild):
    @bot.tree.command(name="profile", description="Get Aarshi's opinion of a user", guild=guild)
    @app_commands.describe(user="The user to profile")
    async def slash_profile(interaction: discord.Interaction, user: discord.Member):
        await _profile(interaction, user)
