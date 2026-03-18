import discord
from utils.roles import is_admin, get_mod_roles, get_admin_roles, add_mod_role, add_admin_role, remove_mod_role, remove_admin_role
from utils.errors import safe_send


class ModRolesView(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=60)
        self.guild = guild
        self._rebuild_selects()

    def _rebuild_selects(self):
        # Remove existing selects to rebuild them
        self.clear_items()

        mod_role_ids = get_mod_roles(self.guild.id)
        admin_role_ids = get_admin_roles(self.guild.id)
        assigned_ids = set(mod_role_ids + admin_role_ids)

        # Unassigned roles for adding
        unassigned = [r for r in self.guild.roles if r.id not in assigned_ids and not r.is_default()]

        if unassigned:
            add_mod_options = [
                discord.SelectOption(label=r.name, value=str(r.id))
                for r in unassigned[:25]
            ]
            add_mod_select = discord.ui.Select(
                placeholder="Add a mod role...",
                options=add_mod_options,
                row=0
            )
            add_mod_select.callback = self.add_mod_callback
            self.add_item(add_mod_select)

            add_admin_options = [
                discord.SelectOption(label=r.name, value=str(r.id))
                for r in unassigned[:25]
            ]
            add_admin_select = discord.ui.Select(
                placeholder="Add an admin role...",
                options=add_admin_options,
                row=1
            )
            add_admin_select.callback = self.add_admin_callback
            self.add_item(add_admin_select)

        # Remove mod role select
        if mod_role_ids:
            mod_roles = [self.guild.get_role(rid) for rid in mod_role_ids if self.guild.get_role(rid)]
            if mod_roles:
                remove_mod_options = [
                    discord.SelectOption(label=f"Remove: {r.name}", value=str(r.id))
                    for r in mod_roles[:25]
                ]
                remove_mod_select = discord.ui.Select(
                    placeholder="Remove a mod role...",
                    options=remove_mod_options,
                    row=2
                )
                remove_mod_select.callback = self.remove_mod_callback
                self.add_item(remove_mod_select)

        # Remove admin role select
        if admin_role_ids:
            admin_roles = [self.guild.get_role(rid) for rid in admin_role_ids if self.guild.get_role(rid)]
            if admin_roles:
                remove_admin_options = [
                    discord.SelectOption(label=f"Remove: {r.name}", value=str(r.id))
                    for r in admin_roles[:25]
                ]
                remove_admin_select = discord.ui.Select(
                    placeholder="Remove an admin role...",
                    options=remove_admin_options,
                    row=3
                )
                remove_admin_select.callback = self.remove_admin_callback
                self.add_item(remove_admin_select)

    def build_embed(self) -> discord.Embed:
        mod_role_ids = get_mod_roles(self.guild.id)
        admin_role_ids = get_admin_roles(self.guild.id)

        def fmt(role_ids):
            if not role_ids:
                return "None assigned"
            roles = [self.guild.get_role(rid) for rid in role_ids]
            return "\n".join(f"• {r.name}" for r in roles if r) or "None found"

        embed = discord.Embed(title="Role Management", color=discord.Color.blurple())
        embed.add_field(name="Mod roles", value=fmt(mod_role_ids), inline=True)
        embed.add_field(name="Admin roles", value=fmt(admin_role_ids), inline=True)
        return embed

    async def add_mod_callback(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            await interaction.response.send_message("You need to be an admin.", ephemeral=True)
            return
        role_id = int(interaction.data["values"][0])
        add_mod_role(self.guild.id, role_id)
        role = self.guild.get_role(role_id)
        self._rebuild_selects()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)
        await interaction.followup.send(f"**{role.name}** added as a mod role.", ephemeral=True)

    async def add_admin_callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only Discord admins can assign admin roles.", ephemeral=True)
            return
        role_id = int(interaction.data["values"][0])
        add_admin_role(self.guild.id, role_id)
        role = self.guild.get_role(role_id)
        self._rebuild_selects()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)
        await interaction.followup.send(f"**{role.name}** added as an admin role.", ephemeral=True)

    async def remove_mod_callback(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            await interaction.response.send_message("You need to be an admin.", ephemeral=True)
            return
        role_id = int(interaction.data["values"][0])
        remove_mod_role(self.guild.id, role_id)
        role = self.guild.get_role(role_id)
        self._rebuild_selects()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)
        await interaction.followup.send(f"**{role.name}** removed from mod roles.", ephemeral=True)

    async def remove_admin_callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only Discord admins can remove admin roles.", ephemeral=True)
            return
        role_id = int(interaction.data["values"][0])
        remove_admin_role(self.guild.id, role_id)
        role = self.guild.get_role(role_id)
        self._rebuild_selects()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)
        await interaction.followup.send(f"**{role.name}** removed from admin roles.", ephemeral=True)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


async def _modroles(interaction: discord.Interaction):
    if not is_admin(interaction.user):
        await safe_send(interaction, "You don't have permission to manage roles.", ephemeral=True)
        return

    view = ModRolesView(interaction.guild)
    embed = view.build_embed()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def setup(bot, guild):
    @bot.tree.command(name="modroles", description="Manage mod and admin roles", guild=guild)
    async def slash_modroles(interaction: discord.Interaction):
        await _modroles(interaction)
