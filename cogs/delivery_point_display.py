# delivery_point_display_cog.py

import discord
from discord.ext import commands, tasks
import json

class DeliveryPointDisplayCog(commands.Cog):
    """Cog to display delivery points dynamically."""

    def __init__(self, bot):
        self.bot = bot
        self.flow_data_file = "data/flow_data.json"
        self.dashboard_channel_id = 1309638065559437375  # Replace with your dashboard channel ID
        self.delivery_point_message_id = None
        self.update_interval = 60  # Update every 60 seconds
        self.update_delivery_points_message.start()  # Start the background task

    def cog_unload(self):
        self.update_delivery_points_message.cancel()

    def load_flow_data(self):
        try:
            with open(self.flow_data_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @commands.Cog.listener()
    async def on_ready(self):
        """Ensure the delivery point message is present on bot startup."""
        dashboard_channel = self.bot.get_channel(self.dashboard_channel_id)

        if not dashboard_channel:
            print("Dashboard channel not found!")
            return

        # Check if the delivery point message already exists
        async for message in dashboard_channel.history(limit=50):
            if message.author == self.bot.user and message.embeds and message.embeds[0].title == "Available Delivery Points":
                self.delivery_point_message_id = message.id
                break
        else:
            # If no delivery point message exists, create one
            embed = await self.create_delivery_points_embed()
            delivery_point_message = await dashboard_channel.send(embed=embed)
            self.delivery_point_message_id = delivery_point_message.id

    @tasks.loop(seconds=60)
    async def update_delivery_points_message(self):
        """Update the delivery points message periodically."""
        if not self.delivery_point_message_id:
            return

        dashboard_channel = self.bot.get_channel(self.dashboard_channel_id)
        if not dashboard_channel:
            print("Dashboard channel not found!")
            return

        try:
            message = await dashboard_channel.fetch_message(self.delivery_point_message_id)
            embed = await self.create_delivery_points_embed()
            await message.edit(embed=embed)
        except discord.NotFound:
            # Message not found; create a new one
            embed = await self.create_delivery_points_embed()
            delivery_point_message = await dashboard_channel.send(embed=embed)
            self.delivery_point_message_id = delivery_point_message.id

    async def create_delivery_points_embed(self):
        """Create an embed displaying the delivery points."""
        flow_data = self.load_flow_data()
        delivery_selection = flow_data.get('delivery_selection', {})
        buttons = delivery_selection.get('buttons', [])

        # Separate stockpiles and facilities
        stockpiles = []
        facilities = []

        for button in buttons:
            is_stockpile = bool(button.get('password'))
            delivery_point = {
                'label': button.get('label', 'Unknown'),
                'hex': button.get('hex', 'Unknown'),
                'location': button.get('location', 'Unknown'),
                'password': button.get('password', '')
            }
            if is_stockpile:
                stockpiles.append(delivery_point)
            else:
                facilities.append(delivery_point)

        # Group by hex
        stockpiles_by_hex = self.group_by_hex(stockpiles)
        facilities_by_hex = self.group_by_hex(facilities)

        # Create the embed
        embed = discord.Embed(
            title="Available Delivery Points",
            description="Below are the current stockpiles and facilities.",
            color=discord.Color.green()
        )

        # Add stockpiles
        if stockpiles_by_hex:
            embed.add_field(name="**____________________Stockpiles____________________**", value="\u200b", inline=False)
            for hex_value, items in stockpiles_by_hex.items():
                field_value = "\n".join(
                    [f"- **{item['label']}** ({item['location']}): {item['password']}" for item in items]
                )
                embed.add_field(name=f"Hex: {hex_value}", value=field_value, inline=False)

        # Add facilities
        if facilities_by_hex:
            embed.add_field(name="**____________________Facilities____________________**", value="\u200b", inline=False)
            for hex_value, items in facilities_by_hex.items():
                field_value = "\n".join(
                    [f"- **{item['label']}** ({item['location']})" for item in items]
                )
                embed.add_field(name=f"Hex: {hex_value}", value=field_value, inline=False)

        embed.set_footer(text="This list updates every minute.")
        return embed

    def group_by_hex(self, delivery_points):
        """Group delivery points by hex."""
        grouped = {}
        for point in delivery_points:
            hex_value = point['hex'] or 'Unknown'
            grouped.setdefault(hex_value, []).append(point)
        return grouped

    @commands.Cog.listener()
    async def on_flow_data_update(self):
        """Event to handle when flow data is updated."""
        await self.update_delivery_points_message()

async def setup(bot):
    await bot.add_cog(DeliveryPointDisplayCog(bot))
