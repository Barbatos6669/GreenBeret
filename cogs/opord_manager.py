import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button

class OrderManagerCog(commands.Cog):
    """Cog to manage OPORD, WARNO, FRAGO, SITREP, and SALUTE creation."""

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
                    "**Create Operational Reports**\n"
                    "Use the buttons below to create an OPORD, WARNO, FRAGO, SITREP, or SALUTE report.\n"
                    "All users can create reports during the testing phase."
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="Click a button below to create a report.")
            mission_wizard_message = await dashboard_channel.send(embed=embed, view=view)
            self.mission_wizard_message_id = mission_wizard_message.id

    def create_mission_wizard_view(self):
        """Create the view for the mission wizard buttons."""
        view = View(timeout=None)

        # Create OPORD Button
        opord_button = Button(
            label="Create OPORD",
            custom_id="create_opord",
            style=discord.ButtonStyle.green
        )
        opord_button.callback = self.create_opord_callback()
        view.add_item(opord_button)

        # Create WARNO Button
        warno_button = Button(
            label="Create WARNO",
            custom_id="create_warno",
            style=discord.ButtonStyle.green
        )
        warno_button.callback = self.create_warno_callback()
        view.add_item(warno_button)

        # Create FRAGO Button
        frago_button = Button(
            label="Create FRAGO",
            custom_id="create_frago",
            style=discord.ButtonStyle.green
        )
        frago_button.callback = self.create_frago_callback()
        view.add_item(frago_button)

        # Create SITREP Button
        sitrep_button = Button(
            label="Create SITREP",
            custom_id="create_sitrep",
            style=discord.ButtonStyle.green
        )
        sitrep_button.callback = self.create_sitrep_callback()
        view.add_item(sitrep_button)

        # Create SALUTE Button
        salute_button = Button(
            label="Create SALUTE Report",
            custom_id="create_salute",
            style=discord.ButtonStyle.green
        )
        salute_button.callback = self.create_salute_callback()
        view.add_item(salute_button)

        return view

    def create_opord_callback(self):
        async def callback(interaction: discord.Interaction):
            # Removed permission check for testing purposes
            modal = OPORDModal(self.bot, self.operations_channel_id)
            await interaction.response.send_modal(modal)

        return callback

    def create_warno_callback(self):
        async def callback(interaction: discord.Interaction):
            # Removed permission check for testing purposes
            modal = WARNOModal(self.bot, self.operations_channel_id)
            await interaction.response.send_modal(modal)

        return callback

    def create_frago_callback(self):
        async def callback(interaction: discord.Interaction):
            # Removed permission check for testing purposes
            modal = FRAGOModal(self.bot, self.operations_channel_id)
            await interaction.response.send_modal(modal)

        return callback

    def create_sitrep_callback(self):
        async def callback(interaction: discord.Interaction):
            # Removed permission check for testing purposes
            modal = SITREPModal(self.bot, self.operations_channel_id)
            await interaction.response.send_modal(modal)

        return callback

    def create_salute_callback(self):
        async def callback(interaction: discord.Interaction):
            # Removed permission check for testing purposes
            modal = SALUTEModal(self.bot, self.operations_channel_id)
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
            label='Sustainment and Command/Signal',
            style=discord.TextStyle.long,
            placeholder='Detail sustainment and command/signal info',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Image URL (optional)',
            style=discord.TextStyle.short,
            placeholder='Provide an image URL (optional)',
            required=False,
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
        embed.add_field(name="4. Sustainment and Command/Signal", value=self.children[3].value or "No information provided.", inline=False)

        # Handle optional image URL
        image_url = self.children[4].value
        if image_url:
            try:
                embed.set_image(url=image_url)
            except Exception as e:
                await interaction.response.send_message(f"Invalid image URL provided: {e}", ephemeral=True)
                return

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
        self.add_item(TextInput(
            label='Image URL (optional)',
            style=discord.TextStyle.short,
            placeholder='Provide an image URL (optional)',
            required=False,
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

        # Handle optional image URL
        image_url = self.children[4].value
        if image_url:
            try:
                embed.set_image(url=image_url)
            except Exception as e:
                await interaction.response.send_message(f"Invalid image URL provided: {e}", ephemeral=True)
                return

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
            label='Service Support and Command/Signal',
            style=discord.TextStyle.long,
            placeholder='Provide service support and command/signal updates',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Image URL (optional)',
            style=discord.TextStyle.short,
            placeholder='Provide an image URL (optional)',
            required=False,
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
        embed.add_field(name="Service Support and Command/Signal", value=self.children[3].value or "No changes.", inline=False)

        # Handle optional image URL
        image_url = self.children[4].value
        if image_url:
            try:
                embed.set_image(url=image_url)
            except Exception as e:
                await interaction.response.send_message(f"Invalid image URL provided: {e}", ephemeral=True)
                return

        embed.set_footer(text=f"Issued by {interaction.user.name}")

        # Send the embed to the operations channel
        await operations_channel.send(embed=embed)

        # Acknowledge the user's submission
        await interaction.response.send_message("FRAGO has been posted to the operations channel.", ephemeral=True)

# Define the SITREPModal class
class SITREPModal(Modal):
    def __init__(self, bot, operations_channel_id):
        super().__init__(title='Create SITREP')
        self.bot = bot
        self.operations_channel_id = operations_channel_id

        # Add TextInput fields for SITREP sections
        self.add_item(TextInput(
            label='Location',
            style=discord.TextStyle.short,
            placeholder='Enter your current location',
            max_length=100
        ))
        self.add_item(TextInput(
            label='Situation Overview',
            style=discord.TextStyle.long,
            placeholder='Provide a brief overview of the situation',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Forces Status',
            style=discord.TextStyle.long,
            placeholder='Status of friendly and enemy forces',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Assessment and Recommendations',
            style=discord.TextStyle.long,
            placeholder='Your assessment and recommendations',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Image URL (optional)',
            style=discord.TextStyle.short,
            placeholder='Provide an image URL (optional)',
            required=False,
            max_length=1024
        ))

    async def on_submit(self, interaction: discord.Interaction):
        # Retrieve the operations channel
        operations_channel = self.bot.get_channel(self.operations_channel_id)
        if not operations_channel:
            await interaction.response.send_message("Error: Operations channel not found.", ephemeral=True)
            return

        # Create an embed for the SITREP
        embed = discord.Embed(
            title="SITUATION REPORT (SITREP)",
            color=discord.Color.teal(),
            timestamp=discord.utils.utcnow()
        )

        # Add fields to the embed
        embed.add_field(name="Location", value=self.children[0].value or "No location provided.", inline=False)
        embed.add_field(name="Situation Overview", value=self.children[1].value or "No information provided.", inline=False)
        embed.add_field(name="Forces Status", value=self.children[2].value or "No information provided.", inline=False)
        embed.add_field(name="Assessment and Recommendations", value=self.children[3].value or "No information provided.", inline=False)

        # Handle optional image URL
        image_url = self.children[4].value
        if image_url:
            try:
                embed.set_image(url=image_url)
            except Exception as e:
                await interaction.response.send_message(f"Invalid image URL provided: {e}", ephemeral=True)
                return

        embed.set_footer(text=f"Reported by {interaction.user.name}")

        # Send the embed to the operations channel
        await operations_channel.send(embed=embed)

        # Acknowledge the user's submission
        await interaction.response.send_message("SITREP has been posted to the operations channel.", ephemeral=True)

# Define the SALUTEModal class
class SALUTEModal(Modal):
    def __init__(self, bot, operations_channel_id):
        super().__init__(title='Create SALUTE Report')
        self.bot = bot
        self.operations_channel_id = operations_channel_id

        # Add TextInput fields for SALUTE sections
        self.add_item(TextInput(
            label='Size and Unit',
            style=discord.TextStyle.short,
            placeholder='Number of personnel or equipment and unit identification',
            max_length=200
        ))
        self.add_item(TextInput(
            label='Activity',
            style=discord.TextStyle.long,
            placeholder='Describe the enemy activity',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Time and Location',
            style=discord.TextStyle.short,
            placeholder='Time of observation and enemy location',
            max_length=200
        ))
        self.add_item(TextInput(
            label='Equipment',
            style=discord.TextStyle.long,
            placeholder='Describe enemy equipment',
            max_length=1024
        ))
        self.add_item(TextInput(
            label='Image URL (optional)',
            style=discord.TextStyle.short,
            placeholder='Provide an image URL (optional)',
            required=False,
            max_length=1024
        ))

    async def on_submit(self, interaction: discord.Interaction):
        # Retrieve the operations channel
        operations_channel = self.bot.get_channel(self.operations_channel_id)
        if not operations_channel:
            await interaction.response.send_message("Error: Operations channel not found.", ephemeral=True)
            return

        # Create an embed for the SALUTE report
        embed = discord.Embed(
            title="SALUTE REPORT",
            color=discord.Color.dark_purple(),
            timestamp=discord.utils.utcnow()
        )

        # Add fields to the embed
        embed.add_field(name="Size and Unit", value=self.children[0].value or "No information provided.", inline=False)
        embed.add_field(name="Activity", value=self.children[1].value or "No information provided.", inline=False)
        embed.add_field(name="Time and Location", value=self.children[2].value or "No information provided.", inline=False)
        embed.add_field(name="Equipment", value=self.children[3].value or "No information provided.", inline=False)

        # Handle optional image URL
        image_url = self.children[4].value
        if image_url:
            try:
                embed.set_image(url=image_url)
            except Exception as e:
                await interaction.response.send_message(f"Invalid image URL provided: {e}", ephemeral=True)
                return

        embed.set_footer(text=f"Reported by {interaction.user.name}")

        # Send the embed to the operations channel
        await operations_channel.send(embed=embed)

        # Acknowledge the user's submission
        await interaction.response.send_message("SALUTE report has been posted to the operations channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(OrderManagerCog(bot))
