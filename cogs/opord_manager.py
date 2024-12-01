import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

class OrderManagerCog(commands.Cog):
    """Cog to manage OPORD, WARNO, and FRAGO creation."""

    def __init__(self, bot):
        self.bot = bot
        self.dashboard_channel_id = 1311021240386981928  # Replace with your dashboard channel ID
        self.operations_channel_id = 1312603657577042000  # Replace with your operations channel ID
        self.mission_wizard_message_id = None  # To store the message ID of the mission wizard message

    @commands.Cog.listener()
    async def on_ready(self):
        """Ensure the mission wizard message is present on bot startup."""
        dashboard_channel = self.bot.get_channel(self.dashboard_channel_id)

        if not dashboard_channel:
            print("Dashboard channel not found!")
            return

        # Register the view
        self.bot.add_view(self.create_mission_wizard_view())

        # Check if the mission wizard message already exists
        async for message in dashboard_channel.history(limit=50):
            if message.author == self.bot.user and message.embeds and message.embeds[0].title == "Mission Wizard":
                self.mission_wizard_message_id = message.id
                break
        else:
            # If no mission wizard message exists, create one
            view = self.create_mission_wizard_view()
            embed = discord.Embed(
                title="Mission Wizard",
                description=(
                    "**Create Operational Orders**\n"
                    "Use the buttons below to create an OPORD, WARNO, or FRAGO.\n"
                    "Only users with the required permissions can create orders."
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="Click a button below to create an order.")
            mission_wizard_message = await dashboard_channel.send(embed=embed, view=view)
            self.mission_wizard_message_id = mission_wizard_message.id

    def create_mission_wizard_view(self):
        """Create the view for the mission wizard buttons."""
        view = discord.ui.View(timeout=None)

        # Create OPORD Button
        opord_button = discord.ui.Button(
            label="Create OPORD",
            custom_id="create_opord",
            style=discord.ButtonStyle.green
        )
        opord_button.callback = self.create_opord_callback()
        view.add_item(opord_button)

        # Create WARNO Button
        warno_button = discord.ui.Button(
            label="Create WARNO",
            custom_id="create_warno",
            style=discord.ButtonStyle.green
        )
        warno_button.callback = self.create_warno_callback()
        view.add_item(warno_button)

        # Create FRAGO Button
        frago_button = discord.ui.Button(
            label="Create FRAGO",
            custom_id="create_frago",
            style=discord.ButtonStyle.green
        )
        frago_button.callback = self.create_frago_callback()
        view.add_item(frago_button)

        return view

    def create_opord_callback(self):
        async def callback(interaction: discord.Interaction):
            # Check if the user has the required permissions
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("You do not have permission to create an OPORD.", ephemeral=True)
                return

            modal = OPORDModal(self.bot, self.operations_channel_id)
            await interaction.response.send_modal(modal)

        return callback

    def create_warno_callback(self):
        async def callback(interaction: discord.Interaction):
            # Check if the user has the required permissions
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("You do not have permission to create a WARNO.", ephemeral=True)
                return

            modal = WARNOModal(self.bot, self.operations_channel_id)
            await interaction.response.send_modal(modal)

        return callback

    def create_frago_callback(self):
        async def callback(interaction: discord.Interaction):
            # Check if the user has the required permissions
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("You do not have permission to create a FRAGO.", ephemeral=True)
                return

            modal = FRAGOModal(self.bot, self.operations_channel_id)
            await interaction.response.send_modal(modal)

        return callback

# Define the OPORDModal class
class OPORDModal(Modal):
    def __init__(self, bot, operations_channel_id):
        super().__init__(title='Create OPORD')
        self.bot = bot
        self.operations_channel_id = operations_channel_id

        # Add TextInput fields for each OPORD section
        self.add_item(TextInput(
            label='Situation',
            style=discord.TextStyle.long,
            placeholder='Describe the situation',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Mission',
            style=discord.TextStyle.long,
            placeholder='State the mission',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Execution',
            style=discord.TextStyle.long,
            placeholder='Outline the execution plan',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Sustainment',
            style=discord.TextStyle.long,
            placeholder='Detail sustainment',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Command and Signal',
            style=discord.TextStyle.long,
            placeholder='Provide command and signal info',
            max_length=1024
        ))

    async def on_submit(self, interaction: discord.Interaction):
        # Retrieve the operations channel
        operations_channel = self.bot.get_channel(self.operations_channel_id)
        if not operations_channel:
            await interaction.response.send_message("Error: Operations channel not found.", ephemeral=True)
            return

        # Create an embed for the OPORD
        embed = discord.Embed(
            title="OPERATION ORDER (OPORD)",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        # Add fields to the embed
        embed.add_field(name="1. Situation", value=self.children[0].value or "No information provided.", inline=False)
        embed.add_field(name="2. Mission", value=self.children[1].value or "No information provided.", inline=False)
        embed.add_field(name="3. Execution", value=self.children[2].value or "No information provided.", inline=False)
        embed.add_field(name="4. Sustainment", value=self.children[3].value or "No information provided.", inline=False)
        embed.add_field(name="5. Command and Signal", value=self.children[4].value or "No information provided.", inline=False)

        embed.set_footer(text=f"Issued by {interaction.user.name}")

        # Send the embed to the operations channel
        await operations_channel.send(embed=embed)

        # Acknowledge the user's submission
        await interaction.response.send_message("OPORD has been posted to the operations channel.", ephemeral=True)

# Define the WARNOModal class
class WARNOModal(Modal):
    def __init__(self, bot, operations_channel_id):
        super().__init__(title='Create WARNO')
        self.bot = bot
        self.operations_channel_id = operations_channel_id

        # Add TextInput fields for WARNO sections
        self.add_item(TextInput(
            label='Situation',
            style=discord.TextStyle.long,
            placeholder='Briefly describe the situation',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Mission',
            style=discord.TextStyle.long,
            placeholder='State the mission',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='General Instructions',
            style=discord.TextStyle.long,
            placeholder='Provide general instructions',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Specific Instructions',
            style=discord.TextStyle.long,
            placeholder='Provide specific instructions',
            max_length=1024
        ))

    async def on_submit(self, interaction: discord.Interaction):
        # Retrieve the operations channel
        operations_channel = self.bot.get_channel(self.operations_channel_id)
        if not operations_channel:
            await interaction.response.send_message("Error: Operations channel not found.", ephemeral=True)
            return

        # Create an embed for the WARNO
        embed = discord.Embed(
            title="WARNING ORDER (WARNO)",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )

        # Add fields to the embed
        embed.add_field(name="Situation", value=self.children[0].value or "No information provided.", inline=False)
        embed.add_field(name="Mission", value=self.children[1].value or "No information provided.", inline=False)
        embed.add_field(name="General Instructions", value=self.children[2].value or "No information provided.", inline=False)
        embed.add_field(name="Specific Instructions", value=self.children[3].value or "No information provided.", inline=False)

        embed.set_footer(text=f"Issued by {interaction.user.name}")

        # Send the embed to the operations channel
        await operations_channel.send(embed=embed)

        # Acknowledge the user's submission
        await interaction.response.send_message("WARNO has been posted to the operations channel.", ephemeral=True)

# Define the FRAGOModal class
class FRAGOModal(Modal):
    def __init__(self, bot, operations_channel_id):
        super().__init__(title='Create FRAGO')
        self.bot = bot
        self.operations_channel_id = operations_channel_id

        # Add TextInput fields for FRAGO sections
        self.add_item(TextInput(
            label='Changes to Situation',
            style=discord.TextStyle.long,
            placeholder='Describe changes to the situation',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Changes to Mission',
            style=discord.TextStyle.long,
            placeholder='Describe changes to the mission',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Execution',
            style=discord.TextStyle.long,
            placeholder='Provide execution details',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Service Support',
            style=discord.TextStyle.long,
            placeholder='Provide service support details',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Command and Signal',
            style=discord.TextStyle.long,
            placeholder='Provide command and signal updates',
            max_length=1024
        ))

    async def on_submit(self, interaction: discord.Interaction):
        # Retrieve the operations channel
        operations_channel = self.bot.get_channel(self.operations_channel_id)
        if not operations_channel:
            await interaction.response.send_message("Error: Operations channel not found.", ephemeral=True)
            return

        # Create an embed for the FRAGO
        embed = discord.Embed(
            title="FRAGMENTARY ORDER (FRAGO)",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )

        # Add fields to the embed
        embed.add_field(name="Changes to Situation", value=self.children[0].value or "No changes.", inline=False)
        embed.add_field(name="Changes to Mission", value=self.children[1].value or "No changes.", inline=False)
        embed.add_field(name="Execution", value=self.children[2].value or "No changes.", inline=False)
        embed.add_field(name="Service Support", value=self.children[3].value or "No changes.", inline=False)
        embed.add_field(name="Command and Signal", value=self.children[4].value or "No changes.", inline=False)

        embed.set_footer(text=f"Issued by {interaction.user.name}")

        # Send the embed to the operations channel
        await operations_channel.send(embed=embed)

        # Acknowledge the user's submission
        await interaction.response.send_message("FRAGO has been posted to the operations channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(OrderManagerCog(bot))
