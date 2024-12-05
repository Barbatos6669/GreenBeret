# stockpile_manager_cog.py

import discord
from discord.ext import commands
import json
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stockpile_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord.stockpile_manager')

class StockpileManagerCog(commands.Cog):
    """Cog to manage stockpile contents and maintain a summary embed."""

    def __init__(self, bot):
        self.bot = bot
        self.flow_data_file = "data/flow_data.json"
        self.categories = [
            "small_arms", "heavy_arms", "heavy_ammunition",
            "utility", "medical", "resource",
            "uniform", "vehicle", "shippable_structure"
        ]
        # Set this to the ID of the channel where you'd like the summary posted.
        self.stockpile_summary_channel_id = 1309638065559437375  # Replace with actual channel ID

        # If you want this to persist across restarts, store and load from file/db.
        self.overview_message_id = None

        logger.info("StockpileManagerCog initialized.")

    def load_flow_data(self):
        """Load JSON data from the flow_data file."""
        try:
            with open(self.flow_data_file, "r") as file:
                data = json.load(file)
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading flow data: {e}")
            return {}

    def save_flow_data(self, flow_data):
        """Save updated JSON data back to the file."""
        try:
            with open(self.flow_data_file, "w") as file:
                json.dump(flow_data, file, indent=4)
                logger.info("Flow data saved successfully.")
        except Exception as e:
            logger.error(f"Error saving flow data: {e}")

    def get_stockpile_data(self, stockpile_name):
        """Retrieve a stockpile entry by label from flow_data."""
        flow_data = self.load_flow_data()
        delivery_buttons = flow_data.get("delivery_selection", {}).get("buttons", [])
        for btn in delivery_buttons:
            if btn["label"].lower() == stockpile_name.lower():
                return btn, flow_data
        return None, flow_data

    @commands.command(name="manage_stockpile")
    async def manage_stockpile(self, ctx, *, stockpile_name: str):
        """Command to manage a given stockpile by name."""
        stockpile_data, flow_data = self.get_stockpile_data(stockpile_name)
        if not stockpile_data:
            await ctx.send(f"No stockpile found with the name `{stockpile_name}`.")
            return

        # We'll loop here allowing multiple add/remove actions until user says no
        while True:
            await ctx.send("Would you like to **Add** or **Remove** items? Type `add`, `remove`, or `done` to finish:")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["add", "remove", "done"],
                    timeout=120
                )
            except asyncio.TimeoutError:
                await ctx.send("Timed out. Please try again.")
                break

            action = msg.content.lower()
            if action == "done":
                # User is done making changes
                break

            if action == "add":
                await self.handle_add(ctx, stockpile_data, flow_data)
            else:
                await self.handle_remove(ctx, stockpile_data, flow_data)

            # After modifications, update the overview
            await self.update_stockpile_overview()

            await ctx.send("Would you like to continue making changes to this stockpile? (yes/no)")
            try:
                cont_msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"],
                    timeout=120
                )
            except asyncio.TimeoutError:
                await ctx.send("Timed out. Ending the process.")
                break

            if cont_msg.content.lower() == "no":
                break

        # After loop ends, we update overview one final time to ensure all changes are reflected
        await self.update_stockpile_overview()

    async def handle_add(self, ctx, stockpile_data, flow_data):
        """Handle adding items to a chosen stockpile."""
        categories_list = '\n'.join([f"- `{cat.replace('_', ' ')}`" for cat in self.categories])
        await ctx.send(
            "Which category would you like to add items to?\n"
            f"{categories_list}"
        )

        try:
            cat_msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=120
            )
        except asyncio.TimeoutError:
            await ctx.send("Timed out. Please try again.")
            return

        chosen_category = cat_msg.content.lower().replace(' ', '_')
        if chosen_category not in self.categories:
            await ctx.send("Invalid category selected. Please start over.")
            return

        category_to_step = {
            "small_arms": "produce_small_arms_items",
            "heavy_arms": "produce_heavy_arms_items",
            "heavy_ammunition": "produce_heavy_ammunition_items",
            "utility": "produce_utility_items",
            "medical": "produce_medical_items",
            "resource": "produce_resource_items",
            "uniform": "produce_uniform_items",
            "vehicle": "produce_vehicle_items",
            "shippable_structure": "produce_shippable_structure_items"
        }

        next_step = category_to_step.get(chosen_category)
        if not next_step:
            await ctx.send("No items defined for this category. Please start over.")
            return

        items_data = flow_data.get(next_step, {})
        items_buttons = items_data.get("buttons", [])
        if not items_buttons:
            await ctx.send("No items found for this category. Please start over.")
            return

        valid_items = [btn["label"] for btn in items_buttons]
        items_list = '\n'.join([f"- `{itm}`" for itm in valid_items])
        await ctx.send(
            f"Select an item to add from `{chosen_category.replace('_', ' ')}`:\n"
            f"{items_list}"
        )

        try:
            item_msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=120
            )
        except asyncio.TimeoutError:
            await ctx.send("Timed out. Please try again.")
            return

        chosen_item = item_msg.content.strip()
        if chosen_item not in valid_items:
            await ctx.send("Invalid item selected. Please start over.")
            return

        await ctx.send(f"How many `{chosen_item}` would you like to add? Enter a number:")
        try:
            qty_msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit(),
                timeout=120
            )
        except asyncio.TimeoutError:
            await ctx.send("Timed out. Please try again.")
            return

        quantity = int(qty_msg.content)
        if quantity <= 0:
            await ctx.send("Quantity must be greater than zero. Please start over.")
            return

        category_list = stockpile_data.get(chosen_category, [])
        for itm in category_list:
            if itm["name"].lower() == chosen_item.lower():
                itm["quantity"] += quantity
                break
        else:
            category_list.append({
                "name": chosen_item,
                "quantity": quantity
            })
        stockpile_data[chosen_category] = category_list
        self.save_flow_data(flow_data)

        await ctx.send(f"Added `{quantity}` of `{chosen_item}` to `{chosen_category.replace('_', ' ')}`.")

    async def handle_remove(self, ctx, stockpile_data, flow_data):
        """Handle removing items from a chosen stockpile."""
        categories_list = '\n'.join([f"- `{cat.replace('_', ' ')}`" for cat in self.categories])
        await ctx.send(
            "From which category would you like to remove items?\n"
            f"{categories_list}"
        )

        try:
            cat_msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=120
            )
        except asyncio.TimeoutError:
            await ctx.send("Timed out. Please try again.")
            return

        chosen_category = cat_msg.content.lower().replace(' ', '_')
        if chosen_category not in self.categories:
            await ctx.send("Invalid category selected. Please start over.")
            return

        category_list = stockpile_data.get(chosen_category, [])
        if not category_list:
            await ctx.send("This category is currently empty. Please start over.")
            return

        current_items = '\n'.join([f"- `{itm['name']}` (Quantity: {itm['quantity']})" for itm in category_list])
        await ctx.send(
            f"Current items in `{chosen_category.replace('_', ' ')}`:\n{current_items}\n"
            "Which item would you like to remove or reduce in quantity?\n"
            "Copy the item name as shown above."
        )

        try:
            item_msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=120
            )
        except asyncio.TimeoutError:
            await ctx.send("Timed out. Please try again.")
            return

        chosen_item = item_msg.content.strip()
        item_entry = None
        for itm in category_list:
            if itm["name"].lower() == chosen_item.lower():
                item_entry = itm
                break

        if not item_entry:
            await ctx.send("Invalid item selected. Please start over.")
            return

        await ctx.send(
            f"Item `{item_entry['name']}` currently has quantity `{item_entry['quantity']}`.\n"
            "Enter the quantity to remove (removing all or more will fully remove the item):"
        )

        try:
            remove_msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit(),
                timeout=120
            )
        except asyncio.TimeoutError:
            await ctx.send("Timed out. Please try again.")
            return

        remove_qty = int(remove_msg.content)
        if remove_qty <= 0:
            await ctx.send("Quantity must be greater than zero. Please start over.")
            return

        if remove_qty >= item_entry["quantity"]:
            category_list.remove(item_entry)
            await ctx.send(f"Removed all `{item_entry['name']}` from `{chosen_category.replace('_', ' ')}`.")
        else:
            item_entry["quantity"] -= remove_qty
            await ctx.send(f"Reduced `{item_entry['name']}` by `{remove_qty}`, now `{item_entry['quantity']}` remain.")

        stockpile_data[chosen_category] = category_list
        self.save_flow_data(flow_data)

        await ctx.send("Stockpile updated successfully.")

    async def update_stockpile_overview(self):
        """Update or create a message in the designated channel listing all stockpiles and their contents in an embed."""
        flow_data = self.load_flow_data()
        delivery_buttons = flow_data.get("delivery_selection", {}).get("buttons", [])

        embed = discord.Embed(
            title="Stockpile Contents Overview",
            description="Below is a list of all available stockpiles and their categorized contents.",
            color=discord.Color.blue()
        )

        if not delivery_buttons:
            embed.add_field(name="No Stockpiles", value="_No stockpiles available._", inline=False)
        else:
            for btn in delivery_buttons:
                stockpile_name = btn["label"]
                lines = []
                for cat in self.categories:
                    cat_list = btn.get(cat, [])
                    if cat_list:
                        cat_display_name = cat.replace('_', ' ').title()
                        lines.append(f"**{cat_display_name}:**")
                        for itm in cat_list:
                            lines.append(f"- {itm['name']} (x{itm['quantity']})")
                        lines.append("")  # spacing

                stockpile_text = "\n".join(lines).strip()
                if not stockpile_text:
                    stockpile_text = "_No items_"
                embed.add_field(name=stockpile_name, value=stockpile_text, inline=False)

        channel = self.bot.get_channel(self.stockpile_summary_channel_id)
        if not channel:
            logger.error("Stockpile summary channel not found. Cannot update overview.")
            return

        if self.overview_message_id is not None:
            try:
                msg = await channel.fetch_message(self.overview_message_id)
                await msg.edit(embed=embed)
            except discord.NotFound:
                new_msg = await channel.send(embed=embed)
                self.overview_message_id = new_msg.id
        else:
            new_msg = await channel.send(embed=embed)
            self.overview_message_id = new_msg.id

        logger.info("Stockpile overview updated with an embed.")

    @commands.Cog.listener()
    async def on_ready(self):
        """Update the overview message when the bot starts."""
        # Wait a moment for the bot to fully connect and fetch channels
        await asyncio.sleep(5)
        await self.update_stockpile_overview()
        logger.info("Stockpile overview updated on bot start.")

async def setup(bot):
    await bot.add_cog(StockpileManagerCog(bot))
    logger.info("StockpileManagerCog loaded successfully.")
