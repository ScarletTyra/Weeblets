import discord
from discord.ext import commands


# ==================================================
# Configuration
# ==================================================

ROLE_ID = 1545572249879191552  # PUT YOUR ROLE ID HERE


# ==================================================
# Auto Role Cog
# ==================================================

class AutoRole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==================================================
    # Member Join Event
    # ==================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        role = member.guild.get_role(ROLE_ID)

        if role is None:

            print(
                f"[AutoRole] Role {ROLE_ID} "
                f"was not found in {member.guild.name}."
            )

            return

        try:

            await member.add_roles(role)

            print(
                f"[AutoRole] Gave '{role.name}' "
                f"to {member}."
            )

        except discord.Forbidden:

            print(
                f"[AutoRole] I don't have permission "
                f"to give '{role.name}'."
            )

        except discord.HTTPException as error:

            print(
                f"[AutoRole] Failed to give role: {error}"
            )


# ==================================================
# Setup
# ==================================================

async def setup(bot):

    await bot.add_cog(
        AutoRole(bot)
    )
