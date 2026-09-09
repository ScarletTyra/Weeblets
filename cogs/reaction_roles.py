import discord
from discord import app_commands
from discord.ext import commands

from database import add_reaction_role, get_reaction_roles


# ==================================================
# Role Button
# ==================================================

class RoleButton(discord.ui.Button):

    def __init__(self, emoji: str, role_id: int):

        super().__init__(
            label="Role",
            emoji=emoji,
            style=discord.ButtonStyle.primary,
            custom_id=f"role_button:{role_id}"
        )

        self.role_id = role_id

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        # --------------------------------------------------
        # Server check
        # --------------------------------------------------

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This can only be used in a server.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Get role
        # --------------------------------------------------

        role = interaction.guild.get_role(
            self.role_id
        )

        if role is None:

            await interaction.response.send_message(
                "❌ This role no longer exists.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Get bot member
        # --------------------------------------------------

        bot_member = interaction.guild.me

        if bot_member is None:

            await interaction.response.send_message(
                "❌ I couldn't find my server member information.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Role hierarchy
        # --------------------------------------------------

        if role >= bot_member.top_role:

            await interaction.response.send_message(
                "❌ I can't manage this role.\n"
                "Move my bot role above the role you're trying to give.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Make sure user is a member
        # --------------------------------------------------

        if not isinstance(
            interaction.user,
            discord.Member
        ):

            await interaction.response.send_message(
                "❌ Couldn't find your server member information.",
                ephemeral=True
            )

            return

        member = interaction.user

        # --------------------------------------------------
        # Add / remove role
        # --------------------------------------------------

        try:

            if role in member.roles:

                await member.remove_roles(
                    role,
                    reason="Reaction role button"
                )

                await interaction.response.send_message(
                    f"❌ Removed **{role.name}**.",
                    ephemeral=True
                )

            else:

                await member.add_roles(
                    role,
                    reason="Reaction role button"
                )

                await interaction.response.send_message(
                    f"✅ Added **{role.name}**!",
                    ephemeral=True
                )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ I don't have permission to manage this role.",
                ephemeral=True
            )

        except discord.HTTPException as error:

            print(
                f"[ReactionRoles] Role error: {error}"
            )

            await interaction.response.send_message(
                "❌ Something went wrong while changing your role.",
                ephemeral=True
            )


# ==================================================
# Persistent Role View
# ==================================================

class RoleView(discord.ui.View):

    def __init__(
        self,
        buttons=None
    ):

        super().__init__(
            timeout=None
        )

        if buttons:

            for emoji, role_id in buttons:

                self.add_item(
                    RoleButton(
                        emoji,
                        role_id
                    )
                )


# ==================================================
# Role Panel Command Group
# ==================================================

class RolePanel(app_commands.Group):

    def __init__(self):

        super().__init__(
            name="rolepanel",
            description="Manage role button panels."
        )

    # ==================================================
    # /rolepanel copy
    # ==================================================

    @app_commands.command(
        name="copy",
        description="Copy a message into a bot-owned role panel."
    )
    @app_commands.describe(
        message_id="The message ID to copy."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def copy(
        self,
        interaction: discord.Interaction,
        message_id: str
    ):

        # --------------------------------------------------
        # Server check
        # --------------------------------------------------

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Convert message ID
        # --------------------------------------------------

        try:

            original_message_id = int(
                message_id
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ Message ID must be a number.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Defer
        # --------------------------------------------------

        await interaction.response.defer(
            ephemeral=True
        )

        # --------------------------------------------------
        # Fetch message
        # --------------------------------------------------

        try:

            original_message = await (
                interaction.channel.fetch_message(
                    original_message_id
                )
            )

        except discord.NotFound:

            await interaction.followup.send(
                "❌ I couldn't find that message.",
                ephemeral=True
            )

            return

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I don't have permission to access that message.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            print(
                f"[ReactionRoles] Fetch error: {error}"
            )

            await interaction.followup.send(
                "❌ Discord returned an error while fetching the message.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Copy content
        # --------------------------------------------------

        content = original_message.content

        # --------------------------------------------------
        # Copy embeds
        # --------------------------------------------------

        embeds = []

        for embed in original_message.embeds:

            try:

                embeds.append(
                    embed.copy()
                )

            except Exception as error:

                print(
                    f"[ReactionRoles] Embed copy error: {error}"
                )

        # --------------------------------------------------
        # Copy attachments
        # --------------------------------------------------

        files = []

        for attachment in original_message.attachments:

            try:

                file = await attachment.to_file()

                files.append(
                    file
                )

            except Exception as error:

                print(
                    f"[ReactionRoles] Attachment copy error: {error}"
                )

        # --------------------------------------------------
        # Check if anything exists
        # --------------------------------------------------

        if (
            not content
            and not embeds
            and not files
        ):

            await interaction.followup.send(
                "❌ There is nothing I can copy from that message.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Send bot-owned copy
        # --------------------------------------------------

        try:

            copied_message = await interaction.channel.send(
                content=content if content else None,
                embeds=embeds if embeds else None,
                files=files if files else None
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I don't have permission to send messages "
                "in this channel.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            print(
                f"[ReactionRoles] Copy send error: {error}"
            )

            await interaction.followup.send(
                "❌ Failed to create the copied message.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Success
        # --------------------------------------------------

        await interaction.followup.send(
            "✅ Message copied successfully!\n\n"
            f"Original message ID: `{original_message.id}`\n"
            f"New message ID: `{copied_message.id}`\n\n"
            "Now use `/rolepanel add` with the **new message ID** "
            "to add role buttons.",
            ephemeral=True
        )

    # ==================================================
    # /rolepanel add
    # ==================================================

    @app_commands.command(
        name="add",
        description="Add a role button to a bot message."
    )
    @app_commands.describe(
        message_id="The message ID of the bot's role panel.",
        emoji="Emoji for the button.",
        role="Role given to the user."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def add(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        role: discord.Role
    ):

        # --------------------------------------------------
        # Respond immediately
        # --------------------------------------------------

        await interaction.response.defer(
            ephemeral=True
        )

        # --------------------------------------------------
        # Server check
        # --------------------------------------------------

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Message ID
        # --------------------------------------------------

        try:

            panel_message_id = int(
                message_id
            )

        except ValueError:

            await interaction.followup.send(
                "❌ Message ID must be a number.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Bot member
        # --------------------------------------------------

        bot_member = guild.me

        if bot_member is None:

            await interaction.followup.send(
                "❌ I couldn't find my bot member.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Role hierarchy
        # --------------------------------------------------

        if role >= bot_member.top_role:

            await interaction.followup.send(
                "❌ I can't manage that role.\n"
                "Move my bot role above it.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Fetch message
        # --------------------------------------------------

        try:

            panel_message = await (
                interaction.channel.fetch_message(
                    panel_message_id
                )
            )

        except discord.NotFound:

            await interaction.followup.send(
                "❌ I couldn't find that message.",
                ephemeral=True
            )

            return

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I can't access that message.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            print(
                f"[ReactionRoles] Message fetch error: {error}"
            )

            await interaction.followup.send(
                "❌ Failed to fetch the message.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Check message ownership
        # --------------------------------------------------

        if interaction.client.user is None:

            await interaction.followup.send(
                "❌ I couldn't identify the bot.",
                ephemeral=True
            )

            return

        if (
            panel_message.author.id
            != interaction.client.user.id
        ):

            await interaction.followup.send(
                "❌ I can only add buttons to messages "
                "sent by me.\n\n"
                "Use `/rolepanel copy` first.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Get existing role buttons
        # --------------------------------------------------

        rows = get_reaction_roles()

        existing = []

        for row in rows:

            if (
                row[0] == guild.id
                and row[1] == interaction.channel.id
                and row[2] == panel_message_id
            ):

                existing.append(
                    row
                )

        # --------------------------------------------------
        # Check duplicates
        # --------------------------------------------------

        for row in existing:

            existing_emoji = row[3]
            existing_role_id = row[4]

            if existing_emoji == emoji:

                await interaction.followup.send(
                    "❌ That emoji is already on this panel.",
                    ephemeral=True
                )

                return

            if existing_role_id == role.id:

                await interaction.followup.send(
                    "❌ That role is already on this panel.",
                    ephemeral=True
                )

                return

        # --------------------------------------------------
        # Button limit
        # --------------------------------------------------

        if len(existing) >= 25:

            await interaction.followup.send(
                "❌ This panel already has 25 buttons.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Save database
        # --------------------------------------------------

        try:

            add_reaction_role(
                guild.id,
                interaction.channel.id,
                panel_message_id,
                emoji,
                role.id
            )

        except Exception as error:

            print(
                f"[ReactionRoles] Database error: {error}"
            )

            await interaction.followup.send(
                "❌ Failed to save the role button.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Build buttons
        # --------------------------------------------------

        buttons = []

        for row in existing:

            buttons.append(
                (
                    row[3],
                    row[4]
                )
            )

        buttons.append(
            (
                emoji,
                role.id
            )
        )

        # --------------------------------------------------
        # Edit message
        # --------------------------------------------------

        try:

            await panel_message.edit(
                view=RoleView(
                    buttons
                )
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I don't have permission to edit this message.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            print(
                f"[ReactionRoles] Edit error: {error}"
            )

            await interaction.followup.send(
                "❌ Discord rejected the message edit.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Register persistent view
        # --------------------------------------------------

        try:

            interaction.client.add_view(
                RoleView(
                    buttons
                ),
                message_id=panel_message_id
            )

        except ValueError:

            # View may already be registered.
            pass

        # --------------------------------------------------
        # Success
        # --------------------------------------------------

        await interaction.followup.send(
            f"✅ Added {emoji} → **{role.name}**",
            ephemeral=True
        )

    # ==================================================
    # /rolepanel list
    # ==================================================

    @app_commands.command(
        name="list",
        description="List role buttons on a panel."
    )
    @app_commands.describe(
        message_id="The message ID of the role panel."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def list_roles(
        self,
        interaction: discord.Interaction,
        message_id: str
    ):

        # --------------------------------------------------
        # Server check
        # --------------------------------------------------

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Message ID
        # --------------------------------------------------

        try:

            panel_message_id = int(
                message_id
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ Invalid message ID.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Get database rows
        # --------------------------------------------------

        rows = get_reaction_roles()

        panel_rows = []

        for row in rows:

            if (
                row[0] == interaction.guild.id
                and row[2] == panel_message_id
            ):

                panel_rows.append(
                    row
                )

        # --------------------------------------------------
        # No roles
        # --------------------------------------------------

        if not panel_rows:

            await interaction.response.send_message(
                "❌ No roles found for this panel.",
                ephemeral=True
            )

            return

        # --------------------------------------------------
        # Build description
        # --------------------------------------------------

        description = ""

        for row in panel_rows:

            emoji = row[3]
            role_id = row[4]

            role = interaction.guild.get_role(
                role_id
            )

            if role:

                description += (
                    f"{emoji} → {role.mention}\n"
                )

            else:

                description += (
                    f"{emoji} → Deleted Role\n"
                )

        # --------------------------------------------------
        # Embed
        # --------------------------------------------------

        embed = discord.Embed(
            title="🎭 Role Panel",
            description=description,
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# ==================================================
# Cog
# ==================================================

class ReactionRoles(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot


# ==================================================
# Setup
# ==================================================

async def setup(bot):

    # --------------------------------------------------
    # Add cog
    # --------------------------------------------------

    await bot.add_cog(
        ReactionRoles(bot)
    )

    # --------------------------------------------------
    # Add /rolepanel command group
    # --------------------------------------------------

    bot.tree.add_command(
        RolePanel()
    )

    # --------------------------------------------------
    # Restore persistent buttons
    # --------------------------------------------------

    rows = get_reaction_roles()

    panels = {}

    for row in rows:

        guild_id = row[0]
        channel_id = row[1]
        message_id = row[2]
        emoji = row[3]
        role_id = row[4]

        key = (
            guild_id,
            channel_id,
            message_id
        )

        if key not in panels:

            panels[key] = []

        panels[key].append(
            (
                emoji,
                role_id
            )
        )

    # --------------------------------------------------
    # Register persistent views
    # --------------------------------------------------

    for key, buttons in panels.items():

        message_id = key[2]

        try:

            bot.add_view(
                RoleView(
                    buttons
                ),
                message_id=message_id
            )

        except Exception as error:

            print(
                f"[ReactionRoles] Failed to restore "
                f"panel {message_id}: {error}"
            )
