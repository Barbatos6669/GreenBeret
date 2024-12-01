import discord
from discord.ext import commands
import json
import uuid


class TaskManager:
    """Manages tasks and their interactions."""

    def __init__(self):
        self.tasks = {}
        self.load_tasks()

    def load_tasks(self):
        try:
            with open("data/tasks.json", "r") as file:
                task_list = json.load(file)
            self.tasks = {task["Task ID"]: task for task in task_list}
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = {}

    def save_tasks(self):
        with open("data/tasks.json", "w") as file:
            json.dump(list(self.tasks.values()), file, indent=4)

    def update_task(self, task_id, task_data):
        self.tasks[task_id] = task_data
        self.save_tasks()

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def get_task_by_message_id(self, message_id):
        for task in self.tasks.values():
            if task.get("Message ID") == message_id:
                return task
        return None

    def get_all_tasks(self):
        return self.tasks.values()


class FlowManagerCog(commands.Cog):
    """Cog to manage reaction-based task flows."""

    def __init__(self, bot):
        self.bot = bot
        self.flow_data = self.load_json("data/flow_data.json")  # Load flow data from JSON
        self.user_states = {}  # Track user progress in flows
        self.user_messages = {}  # Track user specific messages for cleanup
        self.dashboard_message_id = None  # Store the ID of the persistent dashboard message
        self.task_manager = TaskManager()  # Initialize the task manager

    @staticmethod
    def load_json(file_path):
        """Load JSON data from a file."""
        with open(file_path, "r") as file:
            return json.load(file)
        
    def load_flow_data(self):
        """Load flow data from JSON file."""
        try:
            with open("data/flow_data.json", "r") as file:
                self.flow_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading flow data: {e}")
            self.flow_data = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """Ensure the dashboard message is present on bot startup."""
        dashboard_channel_id = 1311021240386981928  # Replace with your dashboard channel ID
        dashboard_channel = self.bot.get_channel(dashboard_channel_id)

        if not dashboard_channel:
            print("Dashboard channel not found!")
            return

        # Register the dashboard view
        self.bot.add_view(self.create_dashboard_view())

        # Check if the dashboard message already exists
        async for message in dashboard_channel.history(limit=10):
            if message.author == self.bot.user and message.embeds and message.embeds[0].title == "Create Task Dashboard":
                self.dashboard_message_id = message.id
                break
        else:
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
                    "You can manage tasks using reactions attached to each task post."
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="Click a button below to start creating tasks.")
            dashboard_message = await dashboard_channel.send(embed=embed, view=view)
            self.dashboard_message_id = dashboard_message.id

    def create_dashboard_view(self):
        """Create the view for the dashboard buttons."""
        view = discord.ui.View(timeout=None)
        for button_data in self.flow_data["dashboard"]["buttons"]:
            button = discord.ui.Button(
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
            self.load_flow_data()  # Reload flow data in case it was updated
            user_id = interaction.user.id
            next_step = button_data.get("next_step")

            if not next_step:
                await interaction.response.send_message("Error: No flow linked to this button.", ephemeral=True)
                return

            # Acknowledge the interaction to prevent "This interaction failed"
            await interaction.response.defer()

            # Initialize user state and start the flow
            flow_type = button_data["custom_id"]  # This will be 'scroop', 'refine', or 'produce'
            self.user_states[user_id] = {
                "current_step": next_step,
                "selections": {},  # Initialize selections as a dictionary
                "flow_type": flow_type  # Store the flow type
            }
            await self.show_step(interaction, next_step)

        return button_callback

    async def show_step(self, interaction, step_name):
        """Show a step based on the JSON and user state."""
        self.load_flow_data()  # Reload flow data in case it was updated
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
        view = discord.ui.View(timeout=None)
        for button_data in step_data["buttons"]:
            button = discord.ui.Button(
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

            if current_step.startswith("produce_") and current_step.endswith("_items"):
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

        # Assign a unique task ID
        task_id = str(uuid.uuid4())
        # Use the stored flow_type
        flow_type = user_state["flow_type"]
        selections = user_state["selections"]

        # Dynamically construct the task based on the flow type
        if flow_type == "scroop":
            task = {
                "Task ID": task_id,
                "Created by": interaction.user.name,
                "Item Needed": selections.get("scroop_resource_selection", "Unknown"),
                "Quantity": selections.get("scroop_quantity_selection", "Unknown"),
                "Delivery Location": selections.get("delivery_selection", "Unknown"),
                "Assigned to": None,
                "Status": "Pending",
            }
        elif flow_type == "refine":
            task = {
                "Task ID": task_id,
                "Created by": interaction.user.name,
                "Item Needed": selections.get("refine_resource_selection", "Unknown"),
                "Quantity": selections.get("refine_quantity_selection", "Unknown"),
                "Delivery Location": selections.get("delivery_selection", "Unknown"),
                "Assigned to": None,
                "Status": "Pending",
            }
        elif flow_type == "produce":
            task = {
                "Task ID": task_id,
                "Created by": interaction.user.name,
                "Category": selections.get("produce_category_selection", "Unknown"),
                "Item Needed": selections.get("produce_item_selection", "Unknown"),
                "Crates Needed": selections.get("produce_quantity_selection", "Unknown"),
                "Delivery Location": selections.get("delivery_selection", "Unknown"),
                "Assigned to": None,
                "Status": "Pending",
            }
        else:
            task = {
                "Task ID": task_id,
                "Created by": interaction.user.name,
                "Item Needed": "Unknown",
                "Quantity": "Unknown",
                "Delivery Location": "Unknown",
                "Assigned to": None,
                "Status": "Pending",
            }

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
            task_description = "\n".join(
                [f"- **{key}:** {value}" for key, value in task.items() if key not in ('Message ID', 'Task ID')]
            )
            embed = discord.Embed(
                title="Task Status: " + task["Status"],
                description=task_description,
                color=get_status_color(task["Status"])
            )
            embed.add_field(
                name="Actions",
                value=(
                    "React with:\n"
                    "🖐️ to **Accept** the task\n"
                    "✅ to **Complete** the task\n"
                    "🛑 to **Abandon** the task"
                ),
                inline=False
            )
            return embed

        # Post the task to the task board
        embed = create_embed()
        message = await task_channel.send(embed=embed)

        # Add reactions to the message
        await message.add_reaction("🖐️")  # Accept Task
        await message.add_reaction("✅")  # Complete Task
        await message.add_reaction("🛑")  # Abandon Task

        # Save the message ID to the task
        task["Message ID"] = message.id

        # Save the task using TaskManager
        self.task_manager.update_task(task_id, task)

        # Cleanup previous user message
        user_id = interaction.user.id
        if user_id in self.user_messages and self.user_messages[user_id]:
            try:
                await self.user_messages[user_id].delete()
            except discord.NotFound:
                pass
            except AttributeError:
                pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return  # Ignore reactions added by the bot itself

        # Get the message ID and check if it matches a task
        message_id = payload.message_id
        task = self.task_manager.get_task_by_message_id(message_id)
        if not task:
            return  # Not a task message

        # Get the emoji used
        emoji = str(payload.emoji)

        # Fetch the channel and message
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            return

        user = self.bot.get_user(payload.user_id)
        if not user:
            return

        # Handle the reaction
        await self.handle_task_reaction(task, message, emoji, user)

    async def handle_task_reaction(self, task, message, emoji, user):
        if emoji == "🖐️":  # Accept Task
            if task["Status"] == "Pending":
                task["Status"] = "In Progress"
                task["Assigned to"] = user.name
                self.task_manager.update_task(task["Task ID"], task)
                await self.update_task_message(task, message)
        elif emoji == "✅":  # Complete Task
            if task["Status"] == "In Progress" and task["Assigned to"] == user.name:
                task["Status"] = "Completed"
                self.task_manager.update_task(task["Task ID"], task)
                await self.update_task_message(task, message)
        elif emoji == "🛑":  # Abandon Task
            if task["Status"] == "In Progress" and task["Assigned to"] == user.name:
                task["Status"] = "Pending"
                task["Assigned to"] = None
                self.task_manager.update_task(task["Task ID"], task)
                await self.update_task_message(task, message)
        else:
            # Remove the reaction if it's not one of the expected ones
            await message.remove_reaction(emoji, user)

    async def update_task_message(self, task, message):
        # Function to get embed color based on task status
        def get_status_color(status):
            colors = {
                "Pending": discord.Color.red(),
                "In Progress": discord.Color.yellow(),
                "Completed": discord.Color.green(),
            }
            return colors.get(status, discord.Color.default())

        # Create the updated embed
        task_description = "\n".join(
            [f"- **{key}:** {value}" for key, value in task.items() if key not in ('Message ID', 'Task ID')]
        )
        embed = discord.Embed(
            title="Task Status: " + task["Status"],
            description=task_description,
            color=get_status_color(task["Status"])
        )
        embed.add_field(
            name="Actions",
            value=(
                "React with:\n"
                "🖐️ to **Accept** the task\n"
                "✅ to **Complete** the task\n"
                "🛑 to **Abandon** the task"
            ),
            inline=False
        )

        # Edit the original message
        await message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(FlowManagerCog(bot))
