# delivery_point_manager_cog.py

import discord
from discord.ext import commands
import json
from discord.ui import Modal, TextInput

class DeliveryPointManagerCog(commands.Cog):
    """Cog to manage delivery points."""

    def __init__(self, bot):
        self.bot = bot
        self.flow_data_file = "data/flow_data.json"
        self.dashboard_channel_id = 1311021240386981928  # Replace with your dashboard channel ID
        self.delivery_point_message_id = None
        self.load_flow_data()

    def load_flow_data(self):
        try:
            with open(self.flow_data_file, "r") as file:
                self.flow_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.flow_data = {}

    def save_flow_data(self):
        with open(self.flow_data_file, "w") as file:
            json.dump(self.flow_data, file, indent=4)

    @commands.Cog.listener()
    async def on_ready(self):
        """Ensure the delivery point message is present on bot startup."""
        dashboard_channel = self.bot.get_channel(self.dashboard_channel_id)

        if not dashboard_channel:
            print("Dashboard channel not found!")
            return

        # Register the delivery point view
        self.bot.add_view(self.create_delivery_point_view())

        # Check if the delivery point message already exists
        async for message in dashboard_channel.history(limit=10):
            if message.author == self.bot.user and message.embeds and message.embeds[0].title == "Delivery Point Management":
                self.delivery_point_message_id = message.id
                break
        else:
            # If no delivery point message exists, create one
            view = self.create_delivery_point_view()
            embed = discord.Embed(
                title="Delivery Point Management",
                description=(
                    "**Manage Your Delivery Points**\n"
                    "Use the buttons below to create new delivery points for tasks.\n"
                    "These delivery points will be available during task creation."
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="Click a button below to add a delivery point.")
            delivery_point_message = await dashboard_channel.send(embed=embed, view=view)
            self.delivery_point_message_id = delivery_point_message.id

    def create_delivery_point_view(self):
        """Create the view for the delivery point buttons."""
        view = discord.ui.View(timeout=None)

        # Create Stockpile Button
        stockpile_button = discord.ui.Button(
            label="Create Stockpile",
            custom_id="create_stockpile",
            style=discord.ButtonStyle.green
        )
        stockpile_button.callback = self.create_stockpile_callback()
        view.add_item(stockpile_button)

        # Create Delivery Point Button
        delivery_point_button = discord.ui.Button(
            label="Create Facility",
            custom_id="create_Facility",
            style=discord.ButtonStyle.green
        )
        delivery_point_button.callback = self.create_delivery_point_callback()
        view.add_item(delivery_point_button)

        return view

    def create_stockpile_callback(self):
        """Callback for 'Create Stockpile' button."""
        async def callback(interaction: discord.Interaction):
            user = interaction.user

            # Define the modal for creating a stockpile
            class StockpileModal(Modal, title='Create Stockpile'):
                name = TextInput(label='Stockpile Name', placeholder='Enter the stockpile name', max_length=50)
                hex = TextInput(label='Hex', placeholder='Enter the map hex', max_length=50)
                location = TextInput(label='Location', placeholder='Enter the town or grid', max_length=50)
                password = TextInput(label='Password', placeholder='Enter the stockpile password', max_length=50)

                async def on_submit(modal_self, modal_interaction: discord.Interaction):
                    # Process the inputs
                    name_value = modal_self.name.value.strip()
                    hex_value = modal_self.hex.value.strip()
                    location_value = modal_self.location.value.strip()
                    password_value = modal_self.password.value.strip()

                    # Generate custom_id
                    custom_id = f"delivery_{name_value.lower().replace(' ', '_')}"

                    # Create the new delivery option
                    new_delivery_option = {
                        "label": name_value,
                        "custom_id": custom_id,
                        "next_step": None,
                        "style": "secondary",
                        "hex": hex_value,
                        "location": location_value,
                        "password": password_value,
                        "small_arms": [],
                        "heavy_arms": [],
                        "heavy_ammunition": [],
                        "utility": [],
                        "medical": [],
                        "resource": [],
                        "uniform": [],
                        "vehicle": [],
                        "shippable_structure": []
                    }

                    # Add to flow_data under 'delivery_selection'
                    if 'delivery_selection' not in self.flow_data:
                        self.flow_data['delivery_selection'] = {"buttons": []}

                    self.flow_data['delivery_selection']['buttons'].append(new_delivery_option)

                    # Save flow_data
                    self.save_flow_data()

                    await modal_interaction.response.send_message(
                        f"Stockpile '{name_value}' added successfully. You may now dismiss this message.",
                        ephemeral=True
                    )

            modal = StockpileModal()
            modal.cog = self  # Pass the cog instance to the modal
            await interaction.response.send_modal(modal)

        return callback

    def create_delivery_point_callback(self):
        """Callback for 'Create Delivery Point' button."""
        async def callback(interaction: discord.Interaction):
            user = interaction.user

            # Define the modal for creating a delivery point
            class DeliveryPointModal(Modal, title='Create Delivery Point'):
                name = TextInput(label='Delivery Point Name', placeholder='Enter the delivery point name', max_length=50)
                hex = TextInput(label='Hex', placeholder='Enter the map hex', max_length=50)
                location = TextInput(label='Location', placeholder='Enter the town or grid', max_length=50)

                async def on_submit(modal_self, modal_interaction: discord.Interaction):
                    # Process the inputs
                    name_value = modal_self.name.value.strip()
                    hex_value = modal_self.hex.value.strip()
                    location_value = modal_self.location.value.strip()

                    # Generate custom_id
                    custom_id = f"delivery_{name_value.lower().replace(' ', '_')}"

                    # Create the new delivery option
                    new_delivery_option = {
                        "label": name_value,
                        "custom_id": custom_id,
                        "next_step": None,
                        "style": "secondary",
                        "hex": hex_value,
                        "location": location_value,
                        "password": "",  # No password for general delivery points
                        "small_arms": [],
                        "heavy_arms": [],
                        "heavy_ammunition": [],
                        "utility": [],
                        "medical": [],
                        "resource": [],
                        "uniform": [],
                        "vehicle": [],
                        "shippable_structure": []
                    }

                    # Add to flow_data under 'delivery_selection'
                    if 'delivery_selection' not in self.flow_data:
                        self.flow_data['delivery_selection'] = {"buttons": []}

                    self.flow_data['delivery_selection']['buttons'].append(new_delivery_option)

                    # Save flow_data
                    self.save_flow_data()

                    await modal_interaction.response.send_message(
                        f"Delivery point '{name_value}' added successfully. You may now dismiss this message.",
                        ephemeral=True
                    )

            modal = DeliveryPointModal()
            modal.cog = self  # Pass the cog instance to the modal
            await interaction.response.send_modal(modal)

        return callback

async def setup(bot):
    await bot.add_cog(DeliveryPointManagerCog(bot))
