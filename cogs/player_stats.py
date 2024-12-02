import json
import discord
from discord.ext import commands, tasks
from pathlib import Path

class PlayerManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = Path("data")  # Path to the data folder
        self.file_path = self.data_folder / "player_data.json"  # Path to the JSON file
        self.players = self.load_data()
        self.leaderboard_channel_id = 1312859293334245376  # Set the channel ID for the leaderboard

    def load_data(self):
        """Load player data from JSON or create a new one if it doesn't exist."""
        if not self.data_folder.exists():
            self.data_folder.mkdir()  # Create the data folder if it doesn't exist

        if self.file_path.exists():
            with open(self.file_path, "r") as file:
                return json.load(file)
        else:
            # Create a new file if it doesn't exist
            data = {"players": {}}
            self.save_data(data)
            return data

    def save_data(self, data=None):
        """Save player data to JSON."""
        if data is None:
            data = self.players
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

    def get_highest_rank(self, member):
        """Determine the highest rank of a member based on their roles."""
        # Define rank-role mapping
        rank_roles = {
            "Polemarchos": 1312632184863199243,  # Replace with actual role IDs
            "Strategos": 1312632139677831238,
            "Hypostrategos": 1312632089648173067,
            "Arkhon": 1312632843448356946,
            "Apomakhos": 1312632035780591657,
            "Eidikos": 1312631992617144420,
            "Hoplites": 1312631928553209948,
            "Helots": 1312631873884651550  # Default rank
        }

        # Sort roles by priority (highest to lowest rank)
        sorted_ranks = sorted(rank_roles.items(), key=lambda x: list(rank_roles.values()).index(x[1]))

        # Check the member's roles against the rank mapping
        for rank, role_id in sorted_ranks:
            if discord.utils.get(member.roles, id=role_id):
                return rank

        # Default to "Helots" if no roles match
        return "Helots"

    def add_player(self, member):
        """Add a new player to the database."""
        if str(member.id) not in self.players["players"]:
            # Determine the player's rank based on their roles
            rank = self.get_highest_rank(member)

            self.players["players"][str(member.id)] = {
                "server_nickname": member.display_name,
                "rank": rank,  # Assign the detected rank
                "war_points": 0,
                "deployments": [],
                "specialties": [],
                "achievements": [],
                "tasks_completed": 0,
                "resources_contributed": 0,
                "medals": [],
                "notes": ""
            }
            self.save_data()

    async def initialize_members(self):
        """Add all current server members to the player database."""
        for guild in self.bot.guilds:
            for member in guild.members:
                if not member.bot:  # Skip bots
                    self.add_player(member)

    @commands.Cog.listener()
    async def on_ready(self):
        """Ensure the database is populated once the bot is ready."""
        await self.initialize_members()
        print("Player database initialized.")
        self.update_leaderboard.start()  # Start the leaderboard update loop

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Automatically add a new member when they join the server."""
        if not member.bot:  # Skip bots
            self.add_player(member)
            print(f"Added new member: {member.display_name}")

    @commands.command(name="show_profile")
    async def show_profile(self, ctx, member: discord.Member = None):
        """Show the profile of a member."""
        member = member or ctx.author  # Default to the command caller
        player_data = self.players["players"].get(str(member.id), None)

        if player_data:
            # Extract medal names for display
            medal_names = [medal["name"] for medal in player_data["medals"]]

            # Create an embed for the profile
            embed = discord.Embed(
                title=f"{player_data['server_nickname']}'s Profile",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=member.avatar.url)  # Add profile picture
            embed.add_field(name="Rank", value=player_data['rank'], inline=False)
            embed.add_field(name="War Points", value=player_data['war_points'], inline=False)
            embed.add_field(name="Deployments", value=", ".join(player_data['deployments']) or "None", inline=False)
            embed.add_field(name="Specialties", value=", ".join(player_data['specialties']) or "None", inline=False)
            embed.add_field(name="Achievements", value=", ".join(player_data['achievements']) or "None", inline=False)
            embed.add_field(name="Tasks Completed", value=player_data['tasks_completed'], inline=False)
            embed.add_field(name="Resources Contributed", value=player_data['resources_contributed'], inline=False)
            embed.add_field(name="Medals", value=", ".join(medal_names) or "None", inline=False)
            embed.add_field(name="Notes", value=player_data['notes'] or "None", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{member.display_name} is not in the database.")


    @commands.command(name="set_leaderboard_channel")
    async def set_leaderboard_channel(self, ctx, channel: discord.TextChannel):
        """Set the leaderboard channel."""
        self.leaderboard_channel_id = channel.id
        await ctx.send(f"Leaderboard channel set to {channel.mention}")

    @tasks.loop(minutes=5)
    async def update_leaderboard(self):
        """Update the leaderboard message in the designated channel."""
        if not self.leaderboard_channel_id:
            return  # Skip if the leaderboard channel is not set

        guild = self.bot.guilds[0]  # Adjust for multi-guild bots
        channel = guild.get_channel(self.leaderboard_channel_id)

        if not channel:
            return  # Skip if the channel no longer exists

        # Sort players by tasks completed
        sorted_players = sorted(
            self.players["players"].values(),
            key=lambda p: p["tasks_completed"],
            reverse=True
        )

        # Create a leaderboard embed
        embed = discord.Embed(
            title="Leaderboard",
            description="Top players ranked by tasks completed",
            color=discord.Color.gold()
        )

        for i, player in enumerate(sorted_players[:10], start=1):  # Top 10 players
            embed.add_field(
                name=f"#{i} {player['server_nickname']}",
                value=f"Rank: {player['rank']}\nTasks Completed: {player['tasks_completed']}",
                inline=False
            )

        # Send or update the leaderboard message
        async for message in channel.history(limit=10):
            if message.author == self.bot.user and message.embeds:
                await message.edit(embed=embed)
                return

        await channel.send(embed=embed)  # Send a new message if no previous one exists


async def setup(bot):
    await bot.add_cog(PlayerManager(bot))
