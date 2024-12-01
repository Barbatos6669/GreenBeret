import discord
from discord.ext import commands
from discord.ui import View, Button
from typing import Dict, List

class PromotionCog(commands.Cog):
    """Cog to handle promotion recommendations and approvals."""

    def __init__(self, bot):
        self.bot = bot
        # Replace with your actual channel IDs
        self.recommendation_channel_id = 1312633165658980433  # Channel where recommendations are posted
        self.promotion_log_channel_id = 1312633074860818452   # Channel where promotions are logged

        # Officer role IDs
        self.officer_role_ids = [
            1312632184863199243,  # ΠΟΛΕΜΑΡΧΟΣ (War Leader)
            1312632139677831238,  # ΣΤΡΑΤΕΓΟΣ (General)
            1312632089648173067,  # ΥΠΟΣΤΡΑΤΕΓΟΣ (Sergeant)
            1312632843448356946,  # ΑΡΚΗΟΝ (Magistrate)
        ]

        # Define the promotion hierarchy (from lowest to highest)
        self.promotion_roles = [
            1312631873884651550,  # ΕΙΛΩΤΕΣ (Recruit)
            1312631928553209948,  # ΟΠΛΙΤΕΣ (Soldier)
            1312631992617144420,  # ΕΙΔΙΚΟΣ (Specialist)
            1312632035780591657,  # ΑΠΟΜΑΧΟΣ (Veteran)
            1312632089648173067,  # ΥΠΟΣΤΡΑΤΕΓΟΣ (Sergeant)
            1312632139677831238,  # ΣΤΡΑΤΕΓΟΣ (General)
            1312632184863199243,  # ΠΟΛΕΜΑΡΧΟΣ (War Leader)
        ]

        self.approval_threshold = 1  # Number of approvals required

        # Keep track of recommendations and their approvals
        self.recommendations: Dict[int, Dict] = {}  # Key: Message ID

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} is ready.")

    @commands.command(name="recommend", help="Recommend a member for promotion.")
    async def recommend(self, ctx, member: discord.Member, *, reason: str):
        """Command for members to recommend someone for promotion."""
        # Check if the member is below the highest rank
        member_top_role = member.top_role
        if member_top_role.id == self.promotion_roles[-1]:
            await ctx.send(f"{member.mention} is already at the highest rank.", delete_after=10)
            return

        # Determine the next promotion role
        try:
            current_role_index = self.promotion_roles.index(member_top_role.id)
            next_role_id = self.promotion_roles[current_role_index + 1]
        except ValueError:
            # Member does not have a promotion role yet
            # Assign the first role in the promotion hierarchy
            next_role_id = self.promotion_roles[0]
            current_role_index = -1  # Indicates no current role

        # Create the embed
        embed = discord.Embed(
            title="Promotion Recommendation",
            description=f"**Member**: {member.mention}\n"
                        f"**Recommended by**: {ctx.author.mention}\n"
                        f"**Current Rank**: {member_top_role.mention if current_role_index != -1 else 'No Rank'}\n"
                        f"**Proposed Rank**: <@&{next_role_id}>\n"
                        f"**Reason**: {reason}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Officers can approve or reject this recommendation.")

        # Create the view with buttons
        view = PromotionApprovalView(self)

        # Send the recommendation to the recommendation channel
        channel = self.bot.get_channel(self.recommendation_channel_id)
        if not channel:
            await ctx.send("Recommendation channel not found.", delete_after=10)
            return

        message = await channel.send(embed=embed, view=view)

        # Store the recommendation data
        self.recommendations[message.id] = {
            "member_id": member.id,
            "proposed_role_id": next_role_id,
            "current_role_index": current_role_index,
            "approvals": [],
            "rejections": [],
            "message_id": message.id,
            "approved": False,
        }

        await ctx.send(f"Recommendation for {member.mention} submitted successfully.", delete_after=10)

    async def handle_approval(self, interaction: discord.Interaction, approve: bool):
        message_id = interaction.message.id
        recommendation = self.recommendations.get(message_id)

        if not recommendation:
            await interaction.response.send_message("Recommendation not found.", ephemeral=True)
            return

        # Check if the user is an officer
        if not any(role.id in self.officer_role_ids for role in interaction.user.roles):
            await interaction.response.send_message("You do not have permission to approve promotions.", ephemeral=True)
            return

        # Prevent multiple approvals from the same officer
        user_id = interaction.user.id
        if user_id in recommendation["approvals"] or user_id in recommendation["rejections"]:
            await interaction.response.send_message("You have already voted on this recommendation.", ephemeral=True)
            return

        if approve:
            recommendation["approvals"].append(user_id)
            await interaction.response.send_message("You have approved this recommendation.", ephemeral=True)
        else:
            recommendation["rejections"].append(user_id)
            await interaction.response.send_message("You have rejected this recommendation.", ephemeral=True)

        # Check if the approval threshold is met
        if len(recommendation["approvals"]) >= self.approval_threshold and not recommendation["approved"]:
            await self.promote_member(recommendation, interaction.message)

    async def promote_member(self, recommendation, message):
        member = message.guild.get_member(recommendation["member_id"])
        if not member:
            await message.channel.send("Member not found.", delete_after=10)
            return

        new_role = message.guild.get_role(recommendation["proposed_role_id"])
        if not new_role:
            await message.channel.send("Role not found.", delete_after=10)
            return

        # Remove the previous rank role if the member has one
        if recommendation["current_role_index"] != -1:
            old_role_id = self.promotion_roles[recommendation["current_role_index"]]
            old_role = message.guild.get_role(old_role_id)
            if old_role in member.roles:
                await member.remove_roles(old_role, reason="Promotion: Removing old rank.")

        # Assign the new role
        await member.add_roles(new_role, reason="Promotion approved by officers.")

        # Update the embed
        embed = message.embeds[0]
        embed.color = discord.Color.green()
        embed.set_footer(text="This recommendation has been approved and the member has been promoted.")

        # Disable the buttons
        view = PromotionApprovalView(self)
        view.disable_buttons()

        await message.edit(embed=embed, view=view)

        # Notify the member
        try:
            await member.send(f"Congratulations! You have been promoted to {new_role.name}.")
        except discord.Forbidden:
            # Couldn't send DM
            pass

        # Log the promotion
        log_channel = self.bot.get_channel(self.promotion_log_channel_id)
        if log_channel:
            await log_channel.send(f"{member.mention} has been promoted to {new_role.mention}.")

        # Mark as approved
        recommendation["approved"] = True

class PromotionApprovalView(View):
    """View containing the approve and reject buttons for promotion recommendations."""

    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

        self.approve_button = Button(
            label="Approve",
            style=discord.ButtonStyle.green,
            custom_id="promotion_approve_button"
        )
        self.approve_button.callback = self.approve_callback

        self.reject_button = Button(
            label="Reject",
            style=discord.ButtonStyle.red,
            custom_id="promotion_reject_button"
        )
        self.reject_button.callback = self.reject_callback

        self.add_item(self.approve_button)
        self.add_item(self.reject_button)

    async def approve_callback(self, interaction: discord.Interaction):
        await self.cog.handle_approval(interaction, approve=True)

    async def reject_callback(self, interaction: discord.Interaction):
        await self.cog.handle_approval(interaction, approve=False)

    def disable_buttons(self):
        self.approve_button.disabled = True
        self.reject_button.disabled = True

async def setup(bot):
    await bot.add_cog(PromotionCog(bot))
