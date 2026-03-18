import discord
from discord import app_commands


async def _help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Aarshi Lodia — Commands",
        description="Ugh, fine. Here's everything I can do. Not that you deserve it.",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Utility", value=(
        "`/help` — You're looking at it\n"
        "`/ping` — Check if I'm even alive\n"
        "`/reload` — Reload a command module"
    ), inline=False)
    embed.add_field(name="Memory & Persona", value=(
        "`/memory` — See what I know about you\n"
        "`/roast @user` — I destroy someone\n"
        "`/profile @user` — My honest opinion of someone"
    ), inline=False)
    embed.add_field(name="Voice", value=(
        "`/join` `/leave` `/say` `/volume` `/skip`"
    ), inline=False)
    embed.add_field(name="Fun", value=(
        "`/opinion` `/mood` `/beef @user`"
    ), inline=False)
    embed.add_field(name="Moderation", value=(
        "`/warn` `/warnings` `/mute` `/unmute` `/kick` `/ban` `/unban` `/purge`"
    ), inline=False)
    embed.add_field(name="Admin", value=(
        "`/setmodrole` `/setadminrole` `/modroles`"
    ), inline=False)
    await interaction.response.send_message(embed=embed)


def setup(bot, guild):
    @bot.tree.command(name="help", description="List all commands", guild=guild)
    async def slash_help(interaction: discord.Interaction):
        await _help(interaction)
