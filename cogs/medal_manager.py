import discord
from discord.ext import commands
import json

class MedalManager(commands.Cog):
    """Cog for managing medals, displaying them, and awarding them to players."""

    def __init__(self, bot):
        self.bot = bot
        self.medal_data_path = "data/medals.json"  # Path to the medal JSON
        self.player_data_path = "data/player_data.json"  # Path to the player JSON
        self.medals = self.load_medal_data()
        self.players = self.load_player_data()

    def load_medal_data(self):
        """Load medal data from a JSON file."""
        try:
            with open(self.medal_data_path, "r") as file:
                return json.load(file)["medals"]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_player_data(self):
        """Save updated player data to a JSON file."""
        with open(self.player_data_path, "w") as file:
            json.dump(self.players, file, indent=4)

    def load_player_data(self):
        """Load player data from a JSON file."""
        try:
            with open(self.player_data_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"players": {}}

    @commands.command(name="show_medal")
    async def show_medal(self, ctx, *, medal_name: str):
        """Display information about a specific medal."""
        medal = next((m for m in self.medals if m["name"].lower() == medal_name.lower()), None)
        if medal:
            embed = discord.Embed(
                title=medal["name"],
                description=medal["description"],
                color=discord.Color.blue()
            )
            embed.add_field(name="Category", value=medal["category"], inline=False)
            embed.add_field(name="War Points", value=str(medal["war_points"]), inline=False)
            if medal["image_url"]:
                embed.set_thumbnail(url=medal["image_url"])
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Medal '{medal_name}' not found.")

    @commands.command(name="give_medal")  # example: !give_medal @user MedalName
    async def give_medal(self, ctx, member: discord.Member, *, medal_name: str):
        """Award a medal to a player."""
        medal = next((m for m in self.medals if m["name"].lower() == medal_name.lower()), None)
        if not medal:
            await ctx.send(f"Medal '{medal_name}' not found.")
            return

        player_id = str(member.id)
        if player_id not in self.players["players"]:
            # Initialize player data if they don't already exist
            self.players["players"][player_id] = {
                "server_nickname": member.display_name,
                "rank": "Helots",
                "war_points": 0,
                "deployments": [],
                "specialties": [],
                "achievements": [],
                "tasks_completed": 0,
                "resources_contributed": 0,
                "medals": [],
                "notes": ""
            }

        player_data = self.players["players"][player_id]

        # Check if the player already has the medal
        if medal["name"] in [m["name"] for m in player_data["medals"]]:
            await ctx.send(f"{member.display_name} already has the '{medal_name}' medal.")
            return

        # Award the medal
        player_data["medals"].append({
            "name": medal["name"],
            "war_points": medal["war_points"]
        })
        player_data["achievements"].append(medal["name"])  # Add medal to achievements
        player_data["war_points"] += medal["war_points"]  # Update war points
        self.save_player_data()

        # Confirm medal assignment
        embed = discord.Embed(
            title=f"Medal Awarded: {medal['name']}",
            description=f"{member.display_name} has been awarded the '{medal_name}' medal.",
            color=discord.Color.gold()
        )
        if medal["image_url"]:
            embed.set_thumbnail(url=medal["image_url"])
        embed.add_field(name="War Points Earned", value=str(medal["war_points"]), inline=False)
        await ctx.send(embed=embed)


    @commands.command(name="achievements") # example: !player_profile @user
    async def player_profile(self, ctx, member: discord.Member = None):
        """Display the player's achievements, including medals and war points."""
        member = member or ctx.author  # Default to the command caller
        player_id = str(member.id)
        player_data = self.players["players"].get(player_id, None)

        if not player_data:
            await ctx.send(f"No data found for {member.display_name}.")
            return

        embed = discord.Embed(
            title=f"{player_data['server_nickname']}'s Profile",
            color=discord.Color.green()
        )
        embed.add_field(name="War Points", value=str(player_data["war_points"]), inline=False)

        medal_list = "\n".join(
            [f"- {m['name']} ({m['war_points']} WP)" for m in player_data["medals"]]
        ) or "No medals earned."
        embed.add_field(name="Medals", value=medal_list, inline=False)

        await ctx.send(embed=embed)
        
    @commands.command(name="medals") # example: !medals
    async def medals(self, ctx):
        """Display a list of all available medals."""
        embed = discord.Embed(
            title="Medals",
            color=discord.Color.gold()
        )
        for medal in self.medals:
            embed.add_field(name=medal["name"], value=medal["description"], inline=False)
        await ctx.send(embed=embed)
        
    # Create a new medal
    @commands.command(name="create_medal")
    async def create_medal(self, ctx):
        """Create a new medal with prompts to avoid user errors."""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        new_medal = {}

        await ctx.send("Please enter the name of the medal.")
        name = await self.bot.wait_for("message", check=check)
        new_medal["name"] = name.content

        await ctx.send("Please enter the description of the medal.")
        description = await self.bot.wait_for("message", check=check)
        new_medal["description"] = description.content

        await ctx.send("Please enter the category of the medal.")
        category = await self.bot.wait_for("message", check=check)
        new_medal["category"] = category.content

        await ctx.send("Please enter the war points of the medal.")
        war_points = await self.bot.wait_for("message", check=check)
        try:
            new_medal["war_points"] = int(war_points.content)
        except ValueError:
            await ctx.send("Invalid input for war points. Please enter an integer value.")
            return

        await ctx.send("Please enter the image URL of the medal (or type 'none' if there is no image).")
        image_url = await self.bot.wait_for("message", check=check)
        new_medal["image_url"] = image_url.content if image_url.content.lower() != 'none' else None

        self.medals.append(new_medal)
        with open(self.medal_data_path, "w") as file:
            json.dump({"medals": self.medals}, file, indent=4)

        await ctx.send(f"Medal '{new_medal['name']}' created successfully.")
        
    @commands.command(name="delete_medal") # example: !delete_medal MedalName
    async def delete_medal(self, ctx, name: str):
        """Delete a medal."""
        medal = next((m for m in self.medals if m["name"].lower() == name.lower()), None)
        if medal:
            self.medals.remove(medal)
            with open(self.medal_data_path, "w") as file:
                json.dump({"medals": self.medals}, file, indent=4)
            await ctx.send(f"Medal '{name}' deleted successfully.")
        else:
            await ctx.send(f"Medal '{name}' not found.")       
        
async def setup(bot):
    await bot.add_cog(MedalManager(bot))
