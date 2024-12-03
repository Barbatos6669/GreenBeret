# mass_order_cog.py

import discord
from discord.ext import commands
import json
import uuid
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mass_order_cog.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord.mass_order_cog')

# Assuming TaskManager is defined in tasks_generator.py within the same directory
from cogs.tasks_generator import TaskManager  # Adjust the import path as necessary

class MassOrderCog(commands.Cog):
    """Cog to handle mass production orders via command-based interactions."""

    def __init__(self, bot):
        self.bot = bot
        self.task_manager = TaskManager()  # Initialize TaskManager
        self.flow_data_file = "data/flow_data.json"
        self.slice_sizes = {
            "small_arms": 20,
            "heavy_arms": 20,
            "heavy_ammunition": 20,
            "utility": 20,
            "medical": 20,
            "resource": 20,
            "vehicle": 3,
            "shippable_structure": 3,          
            # Add other categories and their slice sizes here
        }
        self.task_board_channel_id = 1309637916057800814  # Replace with your task board channel ID
        self.user_states = {}  # To track user progress
        logger.info("MassOrderCog initialized.")

    def load_flow_data(self):
        """Load flow data from JSON file."""
        try:
            with open(self.flow_data_file, "r") as file:
                data = json.load(file)
                logger.info("Flow data loaded successfully.")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading flow data: {e}")
            return {}

    def save_flow_data(self):
        """Save flow data to JSON file."""
        try:
            with open(self.flow_data_file, "w") as file:
                json.dump(self.flow_data, file, indent=4)
                logger.info("Flow data saved successfully.")
        except Exception as e:
            logger.error(f"Error saving flow data: {e}")

    @commands.command(name="mass_order")
    async def mass_order(self, ctx):
        """Command to initiate a mass production order."""
        user_id = ctx.author.id

        if user_id in self.user_states:
            await ctx.send("You already have an ongoing mass order process. Please complete it before starting a new one.")
            logger.warning(f"User {ctx.author} attempted to start a new mass order while one is already in progress.")
            return

        # Initialize user state
        self.user_states[user_id] = {
            "step": "category_selection",
            "orders": []
        }

        # Fetch available sub-categories
        flow_data = self.load_flow_data()
        category_buttons = flow_data.get("produce_category_selection", {}).get("buttons", [])
        valid_categories = [btn["label"] for btn in category_buttons]

        if not valid_categories:
            await ctx.send("No production sub-categories are currently available. Please contact the administrator.")
            logger.error("No sub-categories found in flow_data.json under 'produce_category_selection'.")
            del self.user_states[user_id]
            return

        # Format the list of sub-categories for display
        categories_list = '\n'.join([f"- `{category}`" for category in valid_categories])

        await ctx.send(
            "**Mass Production Order Initiated**\n"
            "Please enter a production sub-category for your order. You can copy and paste one of the following options:\n"
            f"{categories_list}"
        )
        logger.info(f"User {ctx.author} initiated a mass production order.")

        # Wait for the user's response
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=300  # 5 minutes timeout
            )
            sub_category = msg.content.strip()
            await self.process_category_selection(ctx, ctx.author, sub_category)
        except asyncio.TimeoutError:
            del self.user_states[user_id]
            await ctx.send("Mass production order process timed out due to inactivity.")
            logger.info(f"Mass production order timed out for user {ctx.author}.")

    async def process_category_selection(self, ctx, user, sub_category):
        """Process the selected production sub-category and prompt for item selection."""
        user_id = user.id
        if user_id not in self.user_states:
            await ctx.send("No active mass order process found. Please start with `!mass_order`.")
            logger.warning(f"User {user} attempted to process category selection without an active order.")
            return

        # Reload flow_data.json to get the latest data
        flow_data = self.load_flow_data()

        # Validate sub-category
        category_buttons = flow_data.get("produce_category_selection", {}).get("buttons", [])
        valid_categories = [btn["label"] for btn in category_buttons]
        if sub_category not in valid_categories:
            categories_list = '\n'.join([f"- `{category}`" for category in valid_categories])
            await ctx.send(
                f"Invalid sub-category selected. Please enter one of the following options:\n"
                f"{categories_list}"
            )
            logger.warning(f"User {user} entered an invalid sub-category: {sub_category}")
            return

        # Retrieve the next_step corresponding to the selected sub-category
        selected_button = next((btn for btn in category_buttons if btn["label"] == sub_category), None)
        if not selected_button:
            await ctx.send("An error occurred retrieving the selected sub-category. Please try again.")
            logger.error(f"No matching button data found for sub-category: {sub_category}")
            del self.user_states[user_id]
            return

        next_step = selected_button.get("next_step")
        if not next_step:
            await ctx.send("No next step defined for this sub-category. Please contact the administrator.")
            logger.error(f"No next_step defined for sub-category: {sub_category}")
            del self.user_states[user_id]
            return

        self.user_states[user_id]["current_step"] = next_step
        self.user_states[user_id]["selected_category"] = sub_category
        logger.info(f"User {user} selected sub-category: {sub_category}")

        # Fetch available items for the selected sub-category
        items_data = flow_data.get(next_step, {})
        items_buttons = items_data.get("buttons", [])
        valid_items = [btn["label"] for btn in items_buttons]

        if not valid_items:
            await ctx.send("No items are currently available for the selected sub-category. Please contact the administrator.")
            logger.error(f"No items found for step: {next_step}")
            del self.user_states[user_id]
            return

        # Format the list of items for display
        items_list = '\n'.join([f"- `{item}`" for item in valid_items])

        await ctx.send(
            f"**Production Sub-Category Selected:** {sub_category}\n"
            "Please enter an item for this sub-category. You can copy and paste one of the following options:\n"
            f"{items_list}"
        )

        # Wait for the user's response
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == user and m.channel == ctx.channel,
                timeout=300
            )
            item = msg.content.strip()
            await self.process_item_selection(ctx, user, item)
        except asyncio.TimeoutError:
            del self.user_states[user_id]
            await ctx.send("Mass production order process timed out due to inactivity.")
            logger.info(f"Mass production order timed out for user {user}.")

    async def process_item_selection(self, ctx, user, item):
        """Process the selected item and prompt for quantity."""
        user_id = user.id
        if user_id not in self.user_states:
            await ctx.send("No active mass order process found. Please start with `!mass_order`.")
            logger.warning(f"User {user} attempted to process item selection without an active order.")
            return

        # Reload flow_data.json to get the latest data
        flow_data = self.load_flow_data()

        # Retrieve current_step to access the correct items
        current_step = self.user_states[user_id].get("current_step")  # e.g., "produce_small_arms_items"
        items_data = flow_data.get(current_step, {})
        items_buttons = items_data.get("buttons", [])
        valid_items = [btn["label"] for btn in items_buttons]

        if not valid_items:
            await ctx.send("No items available for the selected sub-category. Please contact the administrator.")
            logger.error(f"No items found for step: {current_step}")
            del self.user_states[user_id]
            return

        if item not in valid_items:
            items_list = '\n'.join([f"- `{itm}`" for itm in valid_items])
            await ctx.send(
                f"Invalid item selected. Please enter one of the following options:\n"
                f"{items_list}"
            )
            logger.warning(f"User {user} entered an invalid item: {item}")
            return

        self.user_states[user_id]["current_step"] = "quantity_input"
        self.user_states[user_id]["selected_item"] = item
        logger.info(f"User {user} selected item: {item}")

        await ctx.send(f"**Item Selected:** {item}\nPlease enter the quantity (e.g., `100` max recommended since that is cap):")

        # Wait for the user's response
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == user and m.channel == ctx.channel,
                timeout=300
            )
            quantity_str = msg.content.strip()
            if not quantity_str.isdigit():
                await ctx.send("Invalid quantity. Please enter a numeric value.")
                logger.warning(f"User {user} entered invalid quantity: {quantity_str}")
                return

            quantity = int(quantity_str)
            if quantity <= 0:
                await ctx.send("Quantity must be greater than zero.")
                logger.warning(f"User {user} entered non-positive quantity: {quantity}")
                return

            await self.process_quantity_input(ctx, user, quantity)
        except asyncio.TimeoutError:
            del self.user_states[user_id]
            await ctx.send("Mass production order process timed out due to inactivity.")
            logger.info(f"Mass production order timed out for user {user}.")

    async def process_quantity_input(self, ctx, user, quantity):
        """Process the input quantity and ask if the user wants to add another item."""
        user_id = user.id
        if user_id not in self.user_states:
            await ctx.send("No active mass order process found. Please start with `!mass_order`.")
            logger.warning(f"User {user} attempted to process quantity input without an active order.")
            return

        category = self.user_states[user_id].get("selected_category")
        item_label = self.user_states[user_id].get("selected_item")

        # Add the order to the user's orders list
        self.user_states[user_id]["orders"].append({
            "category": category.lower().replace(' ', '_'),
            "item": item_label,
            "quantity": quantity
        })
        logger.info(f"User {user} added order: {quantity} of {item_label} to {category}")

        await ctx.send(f"Added `{quantity}` of `{item_label}` to `{category}`.\nDo you want to add another item? (Yes/No)")

        # Wait for the user's response
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == user and m.channel == ctx.channel and m.content.lower() in ["yes", "no"],
                timeout=120  # 2 minutes timeout
            )
            response = msg.content.lower()
            if response == "yes":
                self.user_states[user_id]["current_step"] = "category_selection"
                logger.info(f"User {user} chose to add another item.")
                
                # Fetch available sub-categories
                flow_data = self.load_flow_data()
                category_buttons = flow_data.get("produce_category_selection", {}).get("buttons", [])
                valid_categories = [btn["label"] for btn in category_buttons]
                
                if not valid_categories:
                    await ctx.send("No production sub-categories are currently available. Please contact the administrator.")
                    logger.error("No sub-categories found in flow_data.json under 'produce_category_selection'.")
                    del self.user_states[user_id]
                    return

                # Format the list of sub-categories for display
                categories_list = '\n'.join([f"- `{category}`" for category in valid_categories])

                await ctx.send(
                    "Please enter a production sub-category for your order. You can copy and paste one of the following options:\n"
                    f"{categories_list}"
                )
                
                # Wait for the user's response
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author == user and m.channel == ctx.channel,
                        timeout=300
                    )
                    sub_category = msg.content.strip()
                    await self.process_category_selection(ctx, user, sub_category)
                except asyncio.TimeoutError:
                    del self.user_states[user_id]
                    await ctx.send("Mass production order process timed out due to inactivity.")
                    logger.info(f"Mass production order timed out for user {user}.")
            else:
                self.user_states[user_id]["current_step"] = "delivery_location_input"
                logger.info(f"User {user} chose to finalize the order.")
                
                # Fetch available delivery locations
                flow_data = self.load_flow_data()
                delivery_buttons = flow_data.get("delivery_selection", {}).get("buttons", [])
                valid_locations = [btn["label"] for btn in delivery_buttons]
                
                if not valid_locations:
                    await ctx.send("No delivery locations are currently available. Please contact the administrator.")
                    logger.error("No delivery locations found in flow_data.json under 'delivery_selection'.")
                    del self.user_states[user_id]
                    return

                # Format the list of delivery locations for display
                delivery_list = '\n'.join([f"- `{location}`" for location in valid_locations])

                await ctx.send(
                    "Please enter a delivery location for your mass order. You can copy and paste one of the following options:\n"
                    f"{delivery_list}"
                )
                
                # Wait for the user's response
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author == user and m.channel == ctx.channel,
                        timeout=300
                    )
                    delivery_location = msg.content.strip()
                    await self.process_delivery_location_selection(ctx, user, delivery_location)
                except asyncio.TimeoutError:
                    del self.user_states[user_id]
                    await ctx.send("Mass production order process timed out due to inactivity.")
                    logger.info(f"Mass production order timed out for user {user}.")
        except asyncio.TimeoutError:
            del self.user_states[user_id]
            await ctx.send("Mass production order process timed out due to inactivity.")
            logger.info(f"Mass production order timed out for user {user}.")

    async def process_delivery_location_selection(self, ctx, user, delivery_location):
        """Process the selected delivery location, slice the orders, create tasks, and confirm."""
        user_id = user.id
        if user_id not in self.user_states:
            await ctx.send("No active mass order process found.", ephemeral=True)
            logger.warning(f"User {user} attempted to process delivery location without an active order.")
            return

        # Reload flow_data.json to get the latest data
        flow_data = self.load_flow_data()

        # Validate delivery location
        delivery_buttons = flow_data.get("delivery_selection", {}).get("buttons", [])
        valid_locations = [btn["label"] for btn in delivery_buttons]
        if delivery_location not in valid_locations:
            delivery_list = '\n'.join([f"- `{location}`" for location in valid_locations])
            await ctx.send(
                f"Invalid delivery location selected. Please enter one of the following options:\n"
                f"{delivery_list}"
            )
            logger.warning(f"User {user} entered an invalid delivery location: {delivery_location}")
            return

        # Retrieve delivery data
        delivery_data = next(
            (btn for btn in delivery_buttons if btn["label"] == delivery_location), None
        )
        if not delivery_data:
            await ctx.send("Invalid delivery location selected.", ephemeral=True)
            logger.error(f"User {user} selected an invalid delivery location: {delivery_location}")
            return

        hex_location = delivery_data.get("hex")
        password = delivery_data.get("password", "")

        logger.info(f"User {user} selected delivery location: {delivery_location} with hex: {hex_location}")

        # Slice the orders based on slice_sizes
        sliced_tasks = []
        for order in self.user_states[user_id]["orders"]:
            category = order["category"]
            item = order["item"]
            quantity = order["quantity"]

            slice_size = self.slice_sizes.get(category, 5000)  # Default to 5000 if not found
            logger.debug(f"Category: {category}, Slice Size: {slice_size}")  # Debug log
            slices = self.slice_order(quantity, slice_size)

            for slice_qty in slices:
                task = self.create_task(user, category, item, slice_qty, delivery_location, hex_location, password)
                sliced_tasks.append(task)
                logger.info(f"Created sliced task: {slice_qty} of {item} for delivery at {delivery_location}")

        # Post tasks to the task board
        await self.post_tasks_to_board(ctx, sliced_tasks)
        logger.info(f"Posted {len(sliced_tasks)} tasks to the task board for user {user}")

        # Clear the user's state
        del self.user_states[user_id]
        logger.info(f"Cleared user {user}'s state after order finalization.")

        await ctx.send(f"Mass production order processed successfully. Created {len(sliced_tasks)} tasks.")

    def slice_order(self, total: int, slice_size: int):
        """Slice the total quantity into smaller chunks based on slice_size."""
        slices = []
        original_total = total  # Preserve the original total for accurate logging
        while total > 0:
            current_slice = min(slice_size, total)
            slices.append(current_slice)
            total -= current_slice
        logger.debug(f"Sliced total {original_total} into {slices}")
        return slices

    def create_task(self, user: discord.User, category: str, item: str, quantity: int, delivery_location: str, hex_location: str, password: str):
        """Create a task dictionary based on the sliced order."""
        task_id = str(uuid.uuid4())
        task = {
            "Task ID": task_id,
            "Created by": user.name,
            "Category": category.replace('_', ' ').title(),
            "Item Needed": item,
            "Quantity": quantity,
            "Delivery Location": delivery_location,
            "Assigned to": None,
            "Status": "Pending",
            "Message ID": None,  # To be set after posting to the channel
            # Initialize additional fields as empty lists

        }
        # Assign a unique task ID and add to TaskManager
        self.task_manager.update_task(task_id, task)
        logger.info(f"Task {task_id} created for user {user}")
        return task

    async def post_tasks_to_board(self, ctx, tasks):
        """Post all created tasks to the task board channel."""
        task_channel = self.bot.get_channel(self.task_board_channel_id)
        if not task_channel:
            logger.error("Task board channel not found!")
            await ctx.send("Task board channel not found. Please contact the administrator.", ephemeral=True)
            return

        for task in tasks:
            embed = self.create_task_embed(task)
            try:
                message = await task_channel.send(embed=embed)
                await message.add_reaction("🖐️")  # Accept Task
                await message.add_reaction("✅")  # Complete Task
                await message.add_reaction("🛑")  # Abandon Task

                # Save the message ID to the task
                task["Message ID"] = message.id
                self.task_manager.update_task(task["Task ID"], task)
                logger.info(f"Task {task['Task ID']} posted to task board.")

            except Exception as e:
                logger.error(f"Failed to post task {task['Task ID']} to task board: {e}")
                await ctx.send(f"Failed to post task {task['Task ID']} to task board.", ephemeral=True)

    def create_task_embed(self, task):
        """Create an embed for the task."""
        def get_status_color(status):
            colors = {
                "Pending": discord.Color.red(),
                "In Progress": discord.Color.gold(),
                "Completed": discord.Color.green(),
                "Abandoned": discord.Color.dark_red(),
            }
            return colors.get(status, discord.Color.default())

        task_description = "\n".join(
            [f"- **{key.replace('_', ' ').title()}:** {value}" for key, value in task.items() if key not in ('Message ID', 'Task ID')]
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

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle reactions on task messages."""
        # Ignore bot's own reactions
        if user.bot:
            return

        # Get the message the reaction was added to
        message = reaction.message

        # Check if the message ID exists in any task
        task = self.task_manager.get_task_by_message_id(message.id)
        if not task:
            return  # Reaction is not on a task message

        emoji = str(reaction.emoji)

        # Define action based on emoji
        if emoji == "🖐️":
            await self.accept_task(user, task, message)
        elif emoji == "✅":
            await self.complete_task(user, task, message)
        elif emoji == "🛑":
            await self.abandon_task(user, task, message)

    async def accept_task(self, user, task, message):
        """Assign the task to the user."""
        if task["Assigned to"]:
            await user.send(f"Task `{task['Task ID']}` is already assigned to {task['Assigned to']}.")
            logger.info(f"User {user} attempted to accept task {task['Task ID']} which is already assigned.")
            return

        # Assign the task
        task["Assigned to"] = user.name
        task["Status"] = "In Progress"
        self.task_manager.update_task(task["Task ID"], task)

        # Update the embed to reflect assignment
        embed = self.create_task_embed(task)
        await message.edit(embed=embed)
        logger.info(f"Task {task['Task ID']} assigned to user {user}.")

        await user.send(f"You have accepted task `{task['Task ID']}`: {task['Item Needed']} x {task['Quantity']}.")

    async def complete_task(self, user, task, message):
        """Mark the task as completed."""
        if task["Assigned to"] != user.name:
            await user.send(f"You are not assigned to task `{task['Task ID']}`.")
            logger.info(f"User {user} attempted to complete task {task['Task ID']} not assigned to them.")
            return

        # Complete the task
        task["Status"] = "Completed"
        self.task_manager.update_task(task["Task ID"], task)

        # Update the embed to reflect completion
        embed = self.create_task_embed(task)
        await message.edit(embed=embed)
        logger.info(f"Task {task['Task ID']} completed by user {user}.")

        await user.send(f"You have completed task `{task['Task ID']}`: {task['Item Needed']} x {task['Quantity']}.")

    async def abandon_task(self, user, task, message):
        """Mark the task as abandoned."""
        if task["Assigned to"] and task["Assigned to"] != user.name:
            await user.send(f"You cannot abandon task `{task['Task ID']}` as it is assigned to {task['Assigned to']}.")
            logger.info(f"User {user} attempted to abandon task {task['Task ID']} assigned to {task['Assigned to']}.")
            return

        # Abandon the task
        task["Status"] = "Abandoned"
        task["Assigned to"] = None
        self.task_manager.update_task(task["Task ID"], task)

        # Update the embed to reflect abandonment
        embed = self.create_task_embed(task)
        await message.edit(embed=embed)
        logger.info(f"Task {task['Task ID']} abandoned by user {user}.")

        await user.send(f"You have abandoned task `{task['Task ID']}`: {task['Item Needed']} x {task['Quantity']}.")

    @commands.command(name="reload_flow_data")
    @commands.has_role("Admin")  # Replace "Admin" with your desired role name
    async def reload_flow_data(self, ctx):
        """Command to reload flow_data.json."""
        flow_data = self.load_flow_data()
        if flow_data:
            await ctx.send("Flow data reloaded successfully.")
            logger.info(f"Flow data reloaded by user {ctx.author}.")
        else:
            await ctx.send("Failed to reload flow data. Check logs for details.")
            logger.error(f"User {ctx.author} attempted to reload flow data, but it failed.")

async def setup(bot):
    await bot.add_cog(MassOrderCog(bot))
    logger.info("MassOrderCog loaded successfully.")
