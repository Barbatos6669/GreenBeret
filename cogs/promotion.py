import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
from typing import Dict, List
import json

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

        # Promotion point requirements for each rank
        self.war_point_requirements = {
            1312631928553209948: 100,  # ΟΠΛΙΤΕΣ (Soldier)
            1312631992617144420: 2000,  # ΕΙΔΙΚΟΣ (Specialist)
            1312632035780591657: 4000,  # ΑΠΟΜΑΧΟΣ (Veteran)
            1312632089648173067: 60000,  # ΥΠΟΣΤΡΑΤΕΓΟΣ (Sergeant)
            1312632139677831238: 80000,  # ΣΤΡΑΤΕΓΟΣ (General)
            1312632184863199243: 100000, # ΠΟΛΕΜΑΡΧΟΣ (War Leader)
        }

        # Keep track of recommendations and their approvals
        self.recommendations: Dict[int, Dict] = {}  # Key: Message ID

        # Start the auto-promotion check
        self.auto_promotion_check.start()

    @tasks.loop(minutes=1)
    async def auto_promotion_check(self):
        """Automatically recommend members for promotion based on war points."""
        # Wait until the bot is ready
        await self.bot.wait_until_ready()

        if not self.bot.guilds:  # Check if the bot is in any guilds
            print("No guilds found. Skipping auto-promotion check.")
            return

        guild = self.bot.guilds[0]  # Adjust for multi-guild bots
        player_data_path = "data/player_data.json"  # Path to player data JSON

        # Load player data
        try:
            with open(player_data_path, "r") as file:
                players = json.load(file)["players"]
        except (FileNotFoundError, json.JSONDecodeError):
            print("Player data file not found or invalid. Skipping auto-promotion check.")
            return

        # Check each player's war points against their current rank
        for player_id, data in players.items():
            member = guild.get_member(int(player_id))
            if not member:
                continue

            current_rank_id = next(
                (role.id for role in member.roles if role.id in self.promotion_roles), None
            )
            next_rank_id = None
            if current_rank_id:
                # Determine the next rank based on the current rank
                current_index = self.promotion_roles.index(current_rank_id)
                if current_index + 1 < len(self.promotion_roles):
                    next_rank_id = self.promotion_roles[current_index + 1]
            else:
                # No rank, assign the first rank
                next_rank_id = self.promotion_roles[0]

            # Skip if there's no next rank or if they don't meet the war points requirement
            if not next_rank_id or data["war_points"] < self.war_point_requirements[next_rank_id]:
                continue

            # Recommend the player for promotion
            await self.recommend_for_promotion(member, next_rank_id, data["war_points"])

    @auto_promotion_check.before_loop
    async def before_auto_promotion_check(self):
        """Ensure the bot is ready before starting the loop."""
        await self.bot.wait_until_ready()

    async def recommend_for_promotion(self, member, next_role_id, war_points):
        """Automatically recommend a player for promotion."""
        channel = self.bot.get_channel(self.recommendation_channel_id)
        if not channel:
            print("Recommendation channel not found.")
            return

        # Create the embed
        embed = discord.Embed(
            title="Automatic Promotion Recommendation",
            description=f"**Member**: {member.mention}\n"
                        f"**Current War Points**: {war_points}\n"
                        f"**Proposed Rank**: <@&{next_role_id}>",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Officers can approve or reject this recommendation.")

        # Create the view with buttons
        view = PromotionApprovalView(self)

        # Send the recommendation to the recommendation channel
        message = await channel.send(embed=embed, view=view)

        # Store the recommendation data
        self.recommendations[message.id] = {
            "member_id": member.id,
            "proposed_role_id": next_role_id,
            "approvals": [],
            "rejections": [],
            "message_id": message.id,
            "approved": False,
        }

    async def handle_approval(self, interaction: discord.Interaction, approve: bool):
        """Handle approval or rejection of a promotion."""
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
        """Promote a member to the next rank."""
        member = message.guild.get_member(recommendation["member_id"])
        if not member:
            await message.channel.send("Member not found.", delete_after=10)
            return

        new_role = message.guild.get_role(recommendation["proposed_role_id"])
        if not new_role:
            await message.channel.send("Role not found.", delete_after=10)
            return

        # Remove the previous rank role
        for role in member.roles:
            if role.id in self.promotion_roles:
                await member.remove_roles(role, reason="Promotion: Removing old rank.")

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

        # Log the promotion
        log_channel = self.bot.get_channel(self.promotion_log_channel_id)
        if log_channel:
            await log_channel.send(f"{member.mention} has been promoted to {new_role.mention}.")

        # Notify the member
        try:
            await member.send(f"Congratulations! You have been promoted to {new_role.name}.")
        except discord.Forbidden:
            pass

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
