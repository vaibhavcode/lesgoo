import discord


CATEGORIES = {
    "Voice": {
        "description": "Voice channel commands",
        "commands": [
            ("/join", "Join your voice channel"),
            ("/leave", "Leave the voice channel"),
            ("/say", "Make Aarshi say something"),
            ("/volume", "Adjust TTS volume"),
            ("/skip", "Skip Aarshi's current speech"),
        ]
    },
    "Music": {
        "description": "Music playback commands",
        "commands": [
            ("/play", "Play a song or playlist from YouTube"),
            ("/pause", "Pause the current track"),
            ("/resume", "Resume playback"),
            ("/skip", "Skip the current track"),
            ("/stop", "Stop playback and clear queue"),
            ("/queue", "View the music queue"),
            ("/nowplaying", "See what's currently playing"),
            ("/shuffle", "Shuffle the queue"),
            ("/loop", "Toggle looping"),
            ("/volume", "Adjust playback volume"),
        ]
    },
    "Memory": {
        "description": "Memory and persona commands",
        "commands": [
            ("/memory", "See what Aarshi knows about you"),
            ("/clear", "Wipe your conversation history"),
            ("/profile @user", "Get Aarshi's opinion of someone"),
            ("/roast @user", "Have Aarshi roast someone"),
        ]
    },
    "Fun": {
        "description": "Fun and personality commands",
        "commands": [
            ("/opinion", "Get Aarshi's hot take on any topic"),
            ("/mood", "Check Aarshi's current mood"),
            ("/beef @user", "Have Aarshi call someone out"),
        ]
    },
    "Moderation": {
        "description": "Moderation commands — mod role required",
        "commands": [
            ("/warn @user", "Warn a user"),
            ("/warnings @user", "View warnings for a user"),
            ("/mute @user", "Timeout a user"),
            ("/unmute @user", "Remove a timeout"),
            ("/kick @user", "Kick a user"),
            ("/ban @user", "Ban a user"),
            ("/unban", "Unban by user ID"),
            ("/purge", "Delete multiple messages"),
        ]
    },
    "Admin": {
        "description": "Admin commands — admin role required",
        "commands": [
            ("/modroles", "Manage mod and admin roles"),
            ("/setmodrole @role", "Add a mod role"),
            ("/setadminrole @role", "Add an admin role"),
        ]
    },
}


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        options = [
            discord.SelectOption(label=cat, description=data["description"])
            for cat, data in CATEGORIES.items()
        ]
        select = discord.ui.Select(placeholder="Select a category...", options=options)
        select.callback = self.category_callback
        self.add_item(select)

    async def category_callback(self, interaction: discord.Interaction):
        selected = interaction.data["values"][0]
        data = CATEGORIES[selected]
        embed = discord.Embed(
            title=f"{selected} Commands",
            description=data["description"],
            color=discord.Color.blurple()
        )
        for cmd, desc in data["commands"]:
            embed.add_field(name=cmd, value=desc, inline=False)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


def _default_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Aarshi Lodia — Help",
        description="Ugh, fine. Select a category below to see what I can do. Not that you deserve it.",
        color=discord.Color.blurple()
    )
    for cat, data in CATEGORIES.items():
        embed.add_field(name=cat, value=data["description"], inline=True)
    return embed


async def _help(interaction: discord.Interaction):
    view = HelpView()
    embed = _default_embed()
    await interaction.response.send_message(embed=embed, view=view)


def setup(bot, guild):
    @bot.tree.command(name="help", description="List all commands", guild=guild)
    async def slash_help(interaction: discord.Interaction):
        await _help(interaction)
