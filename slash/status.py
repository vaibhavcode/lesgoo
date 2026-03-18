import discord
from utils.memory import get_user_memory
from utils.config import config


async def _status(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_connected():
        members_listening = len(vc.channel.members) - 1
        voice_status = f"Connected to **{vc.channel.name}** ({members_listening} user(s) present)"
    else:
        voice_status = "Not in a voice channel"

    user_mem = get_user_memory(interaction.user.id)
    history_count = len([h for h in user_mem["history"] if h.startswith("User:")])
    persona_notes = len(user_mem["persona_notes"])

    allowed_channel = interaction.guild.get_channel(config["ALLOWED_TEXT_CHANNEL_ID"])
    allowed_name = f"#{allowed_channel.name}" if allowed_channel else "Unknown"

    embed = discord.Embed(title="Aarshi Lodia — Status", color=discord.Color.blurple())
    embed.add_field(name="Voice", value=voice_status, inline=False)
    embed.add_field(name="Listening in", value=allowed_name, inline=True)
    embed.add_field(name="Your messages", value=str(history_count), inline=True)
    embed.add_field(name="Persona notes", value=str(persona_notes), inline=True)
    embed.add_field(
        name="Commands",
        value="Use `/help` to see all available commands.",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


def setup(bot, guild):
    @bot.tree.command(name="status", description="Check Aarshi's current status", guild=guild)
    async def slash_status(interaction: discord.Interaction):
        await _status(interaction)
