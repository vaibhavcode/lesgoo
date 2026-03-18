import discord
from utils.memory import get_user_memory


async def _memory(interaction: discord.Interaction):
    user_mem = get_user_memory(interaction.user.id)
    notes = user_mem["persona_notes"]
    history = user_mem["history"]
    embed = discord.Embed(
        title=f"What Aarshi knows about {interaction.user.display_name}",
        description="Don't flatter yourself. I remember everything.",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Persona notes", value="\n".join(notes) if notes else "Nothing yet.", inline=False)
    embed.add_field(
        name="Recent history (last 6 lines)",
        value=f"```{chr(10).join(history[-6:])}```" if history else "Nothing yet.",
        inline=False
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="memory", description="See what Aarshi knows about you", guild=guild)
    async def slash_memory(interaction: discord.Interaction):
        await _memory(interaction)
