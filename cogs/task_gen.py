import discord
from discord.ext import commands
from discord.ui import Button, View

class DashboardView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Make the view persistent (no timeout)
        self.add_item(Button(label="Scroop", style=discord.ButtonStyle.green, custom_id="scroop"))
        self.add_item(Button(label="Refine", style=discord.ButtonStyle.green, custom_id="refine"))
        self.add_item(Button(label="Produce", style=discord.ButtonStyle.green, custom_id="produce"))
        self.add_item(Button(label="Transport", style=discord.ButtonStyle.green, custom_id="transport"))

class TaskDashboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dashboard_channel_name = "dashboard"  # Replace this with your preferred channel name

    async def find_dashboard_channel(self, guild):
        """Find the dashboard channel in a guild by name."""
        for channel in guild.text_channels:
            if channel.name == self.dashboard_channel_name:
                return channel
        return None

    @commands.Cog.listener()
    async def on_ready(self):
        """Set up the permanent dashboard message in all guilds on bot startup."""
        for guild in self.bot.guilds:
            channel = await self.find_dashboard_channel(guild)
            if channel is None:
                print(f"No channel named '{self.dashboard_channel_name}' in guild: {guild.name}")
                continue

            # Check if the dashboard message already exists
            async for message in channel.history(limit=50):  # Adjust limit if needed
                if message.author == self.bot.user and message.embeds:
                    # Check if the embed title matches "Task Dashboard"
                    if message.embeds[0].title == "Foxhole Task Management Dashboard":
                        print(f"Dashboard message already exists in {guild.name}.")
                        break
            else:
                # Create the embed for the dashboard message
                embed = discord.Embed(
                    title="Foxhole Task Management Dashboard",
                    description=(
                        "Welcome to the **Foxhole Task Management Tool**! This tool is designed to help regiment leaders and veterans "
                        "effectively delegate mission-critical tasks into manageable, bite-sized operations for members throughout the regiment.\n\n"
                        "**Why is this essential?**\n"
                        "🔹 **Efficiency**: By breaking down complex operations into smaller tasks, members can contribute incrementally, ensuring "
                        "critical stockpiles are maintained for regiment-wide operations.\n"
                        "🔹 **Scalability**: Delegating tasks ensures that all members, from the newest recruit to seasoned veterans, can "
                        "actively participate and make meaningful contributions.\n"
                        "🔹 **Preparation**: Proper resource allocation and stockpile management are essential for large-scale operations. "
                        "This system ensures that no mission is hindered due to lack of preparation.\n\n"
                        "Use the buttons below to start assigning tasks and managing resources efficiently:\n\n"
                        "🔹 **Scroop**: Gather raw materials like salvage, components, etc.\n"
                        "🔹 **Refine**: Refine raw materials into usable resources.\n"
                        "🔹 **Produce**: Manufacture equipment or items.\n"
                        "🔹 **Transport**: Move resources or equipment to designated locations."
                    ),
                    color=discord.Color.green()
                )
                embed.set_footer(text="Together, we ensure the regiment's success. Every contribution counts!")
                
                view = DashboardView()
                await channel.send(embed=embed, view=view)
                print(f"Dashboard message set up in {guild.name}.")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle interactions for the dashboard buttons."""
        custom_id = interaction.data.get("custom_id")
        if custom_id in ["scroop", "refine", "produce", "transport"]:
            await interaction.response.send_message(
                f"You selected **{custom_id.capitalize()}**. This feature will be implemented soon!",
                ephemeral=True
            )

# Setup function for adding the cog
async def setup(bot):
    await bot.add_cog(TaskDashboardCog(bot))