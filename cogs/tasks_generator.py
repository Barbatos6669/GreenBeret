import discord
from discord.ext import commands
from discord.ui import View, Button
import json


class FlowManagerCog(commands.Cog):
    """Cog to manage button-based flows."""

    def __init__(self, bot):
        self.bot = bot
        self.flow_data = self.load_json("data/flow_data.json")  # Load flow data from JSON
        self.user_states = {}  # Track user progress in flows
        self.user_messages = {}  # Track user specific messages for cleanup
        self.dashboard_message_id = None  # Store the ID of the persistent dashboard message

    @staticmethod
    def load_json(file_path):
        """Load JSON data from a file."""
        with open(file_path, "r") as file:
            return json.load(file)

    @commands.Cog.listener()
    async def on_ready(self):
        """Ensure the dashboard message is present on bot startup."""
        dashboard_channel_id = 1311021240386981928  # Replace with your dashboard channel ID
        dashboard_channel = self.bot.get_channel(dashboard_channel_id)

        if not dashboard_channel:
            print("Dashboard channel not found!")
            return

        # Register the persistent view
        self.bot.add_view(self.create_dashboard_view())

        # Check if the dashboard message already exists
        async for message in dashboard_channel.history(limit=10):
            if message.author == self.bot.user and message.embeds and message.embeds[0].title == "Create Task Dashboard":
                self.dashboard_message_id = message.id
                return

        # If no dashboard message exists, create one
        view = self.create_dashboard_view()
        embed = discord.Embed(
            title="Create Task Dashboard",
            description=(
                "**Welcome to the Task Management Dashboard!**\n"
                "This board helps you create and manage tasks for your operations.\n\n"
                "**How It Works:**\n"
                "- Use the buttons below to start creating tasks.\n"
                "- Follow the prompts to provide task details such as category, items, and quantity.\n"
                "- Once created, tasks are posted in the task board channel.\n\n"
                "**Task Lifecycle:**\n"
                "Tasks go through the following stages:\n"
                "1. 🟥 **Pending**: Task is awaiting someone to accept it.\n"
                "2. 🟨 **In Progress**: Task is accepted and being worked on.\n"
                "3. 🟩 **Completed**: Task has been successfully finished.\n\n"
                "You can manage tasks using the buttons attached to each task post."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Click a button below to start creating tasks.")
        dashboard_message = await dashboard_channel.send(embed=embed, view=view)
        self.dashboard_message_id = dashboard_message.id


    def create_dashboard_view(self):
        """Create the view for the dashboard buttons."""
        view = View(timeout=None)  # Persistent view
        for button_data in self.flow_data["dashboard"]["buttons"]:
            button = Button(
                label=button_data["label"],
                custom_id=button_data["custom_id"],
                style=getattr(discord.ButtonStyle, button_data["style"].lower(), discord.ButtonStyle.secondary)
            )
            button.callback = self.start_user_flow(button_data)
            view.add_item(button)
        return view

    def start_user_flow(self, button_data):
        """Create a callback to start a user-specific flow."""
        async def button_callback(interaction: discord.Interaction):
            user_id = interaction.user.id
            next_step = button_data.get("next_step")

            if not next_step:
                await interaction.response.send_message("Error: No flow linked to this button.", ephemeral=True)
                return

            # Acknowledge the interaction to prevent "This interaction failed"
            await interaction.response.defer()

            # Initialize user state and start the flow
            self.user_states[user_id] = {
                "current_step": next_step,
                "selections": {}  # Initialize selections as a dictionary
            }
            await self.show_step(interaction, next_step)

        return button_callback


    async def show_step(self, interaction, step_name):
        """Show a step based on the JSON and user state."""
        step_data = self.flow_data.get(step_name)
        if not step_data:
            await interaction.channel.send("Error: Step not found.")
            return

        # Delete the user's previous message, if it exists
        user_id = interaction.user.id
        if user_id in self.user_messages and self.user_messages[user_id]:
            try:
                await self.user_messages[user_id].delete()
            except discord.NotFound:
                pass  # Message already deleted
            except AttributeError:
                pass  # Handle NoneType message gracefully

        # Create buttons for the next step
        view = View(timeout=None)  # Persistent view
        for button_data in step_data["buttons"]:
            button = Button(
                label=button_data["label"],
                custom_id=button_data["custom_id"],
                style=getattr(discord.ButtonStyle, button_data["style"].lower(), discord.ButtonStyle.secondary)
            )
            button.callback = self.create_step_callback(button_data)
            view.add_item(button)

        # Send a new non-ephemeral message and store it for cleanup
        try:
            embed = discord.Embed(title="Choose an option:")
            message = await interaction.channel.send(embed=embed, view=view)
            self.user_messages[user_id] = message  # Save the message for cleanup
        except Exception as e:
            print(f"Error sending message: {e}")

    def create_step_callback(self, button_data):
        async def button_callback(interaction: discord.Interaction):
            user_id = interaction.user.id
            next_step = button_data.get("next_step")

            # Save the current selection in the user's state
            current_step = self.user_states[user_id]["current_step"]

            if current_step in ["produce_small_arms_items", "produce_heavy_arms_items"]:
                # Explicitly save the item selection for Produce flows
                self.user_states[user_id]["selections"]["produce_item_selection"] = button_data["label"]
            elif current_step == "produce_category_selection":
                # Save the category selection for Produce
                self.user_states[user_id]["selections"]["produce_category_selection"] = button_data["label"]
            else:
                # Default behavior for other flows
                self.user_states[user_id]["selections"][current_step] = button_data["label"]

            if next_step:
                # Update user state and show the next step
                self.user_states[user_id]["current_step"] = next_step
                await self.show_step(interaction, next_step)
            else:
                # End the flow and create a task
                await self.create_task(interaction, self.user_states[user_id])

        return button_callback

    async def create_task(self, interaction, user_state):
        """Create a task at the end of a flow, save it to JSON, and post it to the task board."""
        task_board_channel_id = 1309637916057800814  # Replace with your task board channel ID
        task_channel = self.bot.get_channel(task_board_channel_id)

        if not task_channel:
            await interaction.channel.send("Error: Task board channel not found.")
            return

        # Get the flow type (e.g., scroop, refine, produce) from the current step
        flow_type = user_state["current_step"].split("_")[0]
        selections = user_state["selections"]

        # Dynamically construct the task based on the flow type
        if flow_type == "scroop":
            task = {
                "Created by": interaction.user.name,
                "Item Needed": selections.get("scroop_resource_selection", "Unknown"),
                "Quantity": selections.get("scroop_quantity_selection", "Unknown"),
                "Delivery Location": selections.get("scroop_delivery_selection", "Unknown"),
                "Assigned to": None,
                "Status": "Pending",
            }
        elif flow_type == "refine":
            task = {
                "Created by": interaction.user.name,
                "Item Needed": selections.get("refine_resource_selection", "Unknown"),
                "Quantity": selections.get("refine_quantity_selection", "Unknown"),
                "Delivery Location": selections.get("refine_delivery_selection", "Unknown"),
                "Assigned to": None,
                "Status": "Pending",
            }
        elif flow_type == "produce":
            task = {
                "Created by": interaction.user.name,
                "Category": selections.get("produce_category_selection", "Unknown"),
                "Item Needed": selections.get("produce_item_selection", "Unknown"),
                "Crates Needed": selections.get("produce_quantity_selection", "Unknown"),
                "Delivery Location": selections.get("produce_delivery_selection", "Unknown"),
                "Assigned to": None,
                "Status": "Pending",
            }
        else:
            task = {
                "Created by": interaction.user.name,
                "Item Needed": "Unknown",
                "Quantity": "Unknown",
                "Delivery Location": "Unknown",
                "Assigned to": None,
                "Status": "Pending",
            }

        # Save the task to a JSON file
        try:
            with open("data/tasks.json", "r") as file:
                task_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            task_list = []

        task_list.append(task)
        with open("data/tasks.json", "w") as file:
            json.dump(task_list, file, indent=4)

        # Function to get embed color based on task status
        def get_status_color(status):
            colors = {
                "Pending": discord.Color.red(),
                "In Progress": discord.Color.yellow(),
                "Completed": discord.Color.green(),
            }
            return colors.get(status, discord.Color.default())

        # Define the task embed
        def create_embed():
            task_description = "\n".join([f"- **{key}:** {value}" for key, value in task.items()])
            return discord.Embed(
                title="Task Status: " + task["Status"],
                description=task_description,
                color=get_status_color(task["Status"])
            )

        # Define buttons and their callbacks
        view = View()

        # Accept button
        accept_button = Button(label="Accept Task", style=discord.ButtonStyle.green)

        async def accept_callback(interaction: discord.Interaction):
            if task["Status"] == "Pending":
                task["Status"] = "In Progress"
                task["Assigned to"] = interaction.user.name
                with open("data/tasks.json", "w") as file:
                    json.dump(task_list, file, indent=4)
                # Enable Complete and Abandon buttons
                complete_button.disabled = False
                abandon_button.disabled = False
                accept_button.disabled = True
                await interaction.response.edit_message(embed=create_embed(), view=view)

        accept_button.callback = accept_callback
        view.add_item(accept_button)

        # Complete button
        complete_button = Button(label="Complete Task", style=discord.ButtonStyle.primary, disabled=True)

        async def complete_callback(interaction: discord.Interaction):
            if task["Status"] == "In Progress" and task["Assigned to"] == interaction.user.name:
                task["Status"] = "Completed"
                with open("data/tasks.json", "w") as file:
                    json.dump(task_list, file, indent=4)
                # Disable buttons after completion
                complete_button.disabled = True
                abandon_button.disabled = True
                await interaction.response.edit_message(embed=create_embed(), view=view)

        complete_button.callback = complete_callback
        view.add_item(complete_button)

        # Abandon button
        abandon_button = Button(label="Abandon Task", style=discord.ButtonStyle.danger, disabled=True)

        async def abandon_callback(interaction: discord.Interaction):
            if task["Status"] == "In Progress" and task["Assigned to"] == interaction.user.name:
                task["Status"] = "Pending"
                task["Assigned to"] = None
                task["Message ID"] = interaction.message.id  # Add this line to save the message ID
                with open("data/tasks.json", "w") as file:
                    json.dump(task_list, file, indent=4)
                # Reset buttons to initial state
                accept_button.disabled = False
                complete_button.disabled = True
                abandon_button.disabled = True
                await interaction.response.edit_message(embed=create_embed(), view=view)

        abandon_button.callback = abandon_callback
        view.add_item(abandon_button)

        # Post the task to the task board
        message = await task_channel.send(embed=create_embed(), view=view)

        # Save the message ID to the task
        task["Message ID"] = message.id
        with open("data/tasks.json", "w") as file:
            json.dump(task_list, file, indent=4)

        # Cleanup previous user message
        user_id = interaction.user.id
        if user_id in self.user_messages and self.user_messages[user_id]:
            try:
                await self.user_messages[user_id].delete()
            except discord.NotFound:
                pass
            except AttributeError:
                pass


async def setup(bot):
    await bot.add_cog(FlowManagerCog(bot))