import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import json

# Create stockpile button
class StockpileView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Create Stockpile", style=discord.ButtonStyle.green, custom_id="create_stockpile"))

# Creates a form for the stock pile to fill out generl information
class StockpileModal(Modal):
    def __init__(self, cog, channel):
        super().__init__(title="Create Stockpile")
        self.cog = cog
        self.channel = channel

        self.name = TextInput(label="Name")
        self.hex = TextInput(label="Hex")
        self.location = TextInput(label="Location")
        self.password = TextInput(label="Password", style=discord.TextStyle.short)

        self.add_item(self.name)
        self.add_item(self.hex)
        self.add_item(self.location)
        self.add_item(self.password)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        hex = self.hex.value
        location = self.location.value
        password = self.password.value

        if name in self.cog.stockpiles:
            await interaction.response.send_message(f"Stockpile with name {name} already exists.", ephemeral=True)
        else:
            embed = discord.Embed(
                title=f"Stockpile: {name}",
                description=f"**Name:** {name}\n**Hex:** {hex}\n**Location:** {location}\n**Password:** {password}",
                color=discord.Color.blue()
            )
            view = StockpileActionView(self.cog, name)
            message = await self.channel.send(embed=embed, view=view)

            self.cog.stockpiles[name] = {
                "name": name,
                "hex": hex,
                "location": location,
                "password": password,
                "message_id": message.id
            }
            self.cog.save_stockpiles()

            await interaction.response.send_message(f"Stockpile {name} created successfully.", ephemeral=True)

# Allows a user to delete the stockpile from the chat and the json dynamically
class StockpileActionView(View):
    def __init__(self, cog, stockpile_name):
        super().__init__(timeout=None)
        self.cog = cog
        self.stockpile_name = stockpile_name

        self.add_item(Button(label="Delete", style=discord.ButtonStyle.danger, custom_id=f"delete_{stockpile_name}"))

# Main class for the stockpile cog
class StockpileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stockpiles = self.load_stockpiles()

    def load_stockpiles(self):
        try:
            with open("data/stockpiles.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_stockpiles(self):
        with open("data/stockpiles.json", "w") as f:
            json.dump(self.stockpiles, f, indent=4)

    # Set up the dashboard message in all guilds on bot startup
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            channel = discord.utils.get(guild.text_channels, name="stockpiles")
            if channel is None:
                print(f"No channel named 'stockpiles' in guild: {guild.name}")
                continue

            async for message in channel.history(limit=50):
                if message.author == self.bot.user and message.embeds:
                    if message.embeds[0].title == "Stockpile Management Dashboard":
                        print(f"Dashboard message already exists in {guild.name}.")
                        break
            else:
                embed = discord.Embed(
                    title="Stockpile Management Dashboard",
                    description="Use the button below to create a new stockpile.",
                    color=discord.Color.green(),
                )
                view = StockpileView()
                await channel.send(embed=embed, view=view)
                print(f"Dashboard message set up in {guild.name}.")

    # Allows the user to interact with the stockpile
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        custom_id = interaction.data.get("custom_id")
        if custom_id == "create_stockpile":
            modal = StockpileModal(self, interaction.channel)
            await interaction.response.send_modal(modal)
        elif custom_id.startswith("delete_"):
            stockpile_name = custom_id[len("delete_"):]
            if stockpile_name in self.stockpiles:
                del self.stockpiles[stockpile_name]
                self.save_stockpiles()
                await interaction.message.delete()
                await interaction.response.send_message(
                    f"Stockpile '{stockpile_name}' deleted successfully.", ephemeral=True
                )

# Set up the cog                       
async def setup(bot):
    await bot.add_cog(StockpileCog(bot))