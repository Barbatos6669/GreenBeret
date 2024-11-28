import discord
from discord.ext import commands
from discord.ui import Button, View
import logging

# inport the buttons from the buttons.py file
from cogs.buttons import DashboardView, ScroopButtonView, ScroopQuantityButtonView, DeliveryButtonView, RefineButtonView, ProduceButtonView, SmallArmsButtonView, HeavyArmsButtonView, HeavyAmmunitionButtonView, UtilityButtonView, ResourceButtonView, MedicalButtonView, UniformsButtonView, VehiclesButtonView, ShippableStructureButtonView, CrateQuantityButtonView, RefineQuantityButtonView

# Add this at the beginning of your file to configure logging
logging.basicConfig(level=logging.INFO)

# List of custom_ids
scroop_custom_ids = ["salvage", "components", "sulfur", "coal"]
scroop_quantity_custom_ids = ["salvage_scroop_1500", "salvage_scroop_2500", "salvage_scroop_5000", "components_scroop_1500", "components_scroop_2500", "components_scroop_5000", "sulfur_scroop_1500", "sulfur_scroop_2500", "sulfur_scroop_5000", "coal_scroop_1500", "coal_scroop_2500", "coal_scroop_5000"]

refine_custom_ids = ["refine_basic_materials", "refine_diesel", "refine_explosive_powder", "refine_refined_materials", "refine_heavy_explosive_powder", "refine_gravel"]
refine_quantity_custom_ids = ["refine_basic_materials_refine_1500", "refine_basic_materials_refine_2500", "refine_basic_materials_refine_5000", "refine_diesel_refine_1500", "refine_diesel_refine_2500", "refine_diesel_refine_5000", "refine_explosive_powder_refine_1500", "refine_explosive_powder_refine_2500", "refine_explosive_powder_refine_5000", "refine_refined_materials_refine_1500", "refine_refined_materials_refine_2500", "refine_refined_materials_refine_5000", "refine_heavy_explosive_powder_refine_1500", "refine_heavy_explosive_powder_refine_2500", "refine_heavy_explosive_powder_refine_5000", "refine_gravel_refine_1500", "refine_gravel_refine_2500", "refine_gravel_refine_5000"]

produce_custom_ids = ["produce_small_arms", "produce_heavy_arms", "produce_heavy_ammunition", "produce_utility", "produce_resource", "produce_medical", "produce_uniforms", "produce_vehicles", "produce_shippable_structure"]

# item categories list
small_arms_custom_ids = ["produce_small_arms_dusk_ce_iii", "produce_small_arms_792mm", "produce_small_arms_catara_mo_ii", "produce_small_arms_krn886_127_gast_machine_gun", "produce_small_arms_bomastone_granade", "produce_small_arms_8mm", "produce_small_arms_cometa_t2_9", "produce_small_arms_44", "produce_small_arms_catena_rt_iv_autorifle", "produce_small_arms_argenti_r_ii_rifle", "produce_small_arms_volta_r_i_repeater", "produce_small_arms_fuscina_pi_i", "produce_small_arms_krr2_790_omen", "produce_small_arms_krr3_792_auger", "produce_small_arms_762", "produce_small_arms_krd1_750_dragonfly", "produce_small_arms_buckshot", "produce_small_arms_the_pitch_gun_mc_v", "produce_small_arms_lionclaw_mc_viii", "produce_small_arms_9mm", "produce_small_arms_pt_815_smoke_granade", "produce_small_arms_green_ash_grenade", "produce_small_arms_127mm"]
heavy_arms_custom_ids = ["produce_heavy_arms_typhon_ra_xii", "produce_heavy_arms_20mm", "produce_heavy_arms_venom_c_iii_35", "produce_heavy_arms_bane_45", "produce_heavy_arms_ap_rpg", "produce_heavy_arms_arc_rpg", "produce_heavy_arms_molten_wind_v_11_flame_torch", "produce_heavy_arms_klg901_2_lunair_f", "produce_heavy_arms_mounted_fissura_gd_i", "produce_heavy_arms_tremola_grenade_gpb_1", "produce_heavy_arms_lamentum_mm_iv", "produce_heavy_arms_daucus_isg_iii", "produce_heavy_arms_30mm", "produce_heavy_arms_cremari_mortar", "produce_heavy_arms_flare_mortar_shell", "produce_heavy_arms_shrapnel_mortar_shell", "produce_heavy_arms_mortar_shell", "produce_heavy_arms_ignifist_30", "produce_heavy_arms_mammon_91_b", "produce_heavy_arms_anti_tank_sticky_bomb", "produce_heavy_arms_rpg"]
heavy_ammunition_custom_ids = ["produce_heavy_ammunition_150mm", "produce_heavy_ammunition_120mm", "produce_heavy_ammunition_250mm", "produce_heavy_ammunition_68mm", "produce_heavy_ammunition_40mm"] 
utility_custom_ids = ["produce_utility_barbed_wire", "produce_utility_buckhorn_ccq_18", "produce_utility_binoculars", "produce_utility_hydras_whisper", "produce_utility_havoc_charge", "produce_utility_molten_wind_v_ii_ammo", "produce_utility_listening_kit", "produce_utility_metal_beam", "produce_utility_radio_backpack", "produce_utility_sandbag", "produce_utility_havoc_charge_denotator", "produce_utility_shovel", "produce_utility_sledge_hammer", "produce_utility_tripod", "produce_utility_wind_stock", "produce_utility_wrench", "produce_utility_water_bucket", "produce_utility_gas_mask", "produce_utility_gas_mask_filter", "produce_utility_radio"]
resource_custom_ids = ["produce_resource_maintenance_supplies"]
medical_custom_ids = ["produce_medical_bandage", "produce_medical_first_aid_kit", "produce_medical_trauma_kit", "produce_medical_blood_plasma", "produce_medical_soldier_supplies"]
uniforms_custom_ids = ["produce_uniforms_vilian_flak_vest", "produce_uniforms_fabri_rucksack", "produce_uniforms_grenadiers_baldric", "produce_uniforms_medic_fatigues", "produce_uniforms_officialis_attire", "produce_uniforms_legionarys_oilcoat", "produce_uniforms_recon_camo", "produce_uniforms_heavy_topcoat", "produce_uniforms_tankmans_coveralls"]
vehicles_custom_ids = ["produce_vehicles_r_12_salus_ambulance", "produce_vehicles_t3_xiphos", "produce_vehicles_r_15_chariot", "produce_vehicles_aa_2_battering_ram", "produce_vehicles_g40_sagittarii", "produce_vehicles_bms_packmule_flatbed", "produce_vehicles_hh_a_javelin", "produce_vehicles_ab_8_acheron", "produce_vehicles_120_68_koronides_field_gun", "produce_vehicles_hc_2_scorpion", "produce_vehicles_h_5_hatchet", "produce_vehicles_86k_a_bardiche", "produce_vehicles_90t_v_nemesis", "produce_vehicles_85k_b_falchion", "produce_vehicles_03mm_caster", "produce_vehicles_r_5_atlas_hauler", "produce_vehicles_rr_3_stolon_tanker", "produce_vehicles_r_1_hauler", "produce_vehicles_t12_actaeon_tankette", "produce_vehicles_uv_05a_argonaut", "produce_vehicles_roster_0_junkwagon"]
shippable_structure_custom_ids = ["produce_shippable_structure_50_500_thunderbolt_cannon", "produce_shippable_structure_material_pallet", "produce_shippable_structure_resource_container", "produce_shippable_structure_shipping_container", "produce_shippable_structure_dae_1o_3_polybolos", "produce_shippable_structure_concrete_mixer", "produce_shippable_structure_liquid_container"]

# TaskDashboardCog class
class TaskDashboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dashboard_channel_name = "dashboard"  # Replace this with your preferred channel name

    # looks for the dashboard channel in the guild
    async def find_dashboard_channel(self, guild):
        """Find the dashboard channel in a guild by name."""
        for channel in guild.text_channels:
            if channel.name == self.dashboard_channel_name:
                return channel
        return None

    # sets up the dashboard message in all guilds on bot startup
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
    
    # handles user interactions
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle interactions for the dashboard buttons."""
        custom_id = interaction.data.get("custom_id")
        print(f"Received interaction with custom_id: {custom_id}")  # Debug log

        if custom_id == "scroop":
            # Show Scroop resource selection
            await interaction.response.send_message(
                "You selected **Scroop**. Please choose a resource:",
                view=ScroopButtonView(),
                ephemeral=True
            )
        elif custom_id == "refine":
            # Show Refine resource selection
            await interaction.response.send_message(
                "You selected **Refine**. Please choose a resource:",
                view=RefineButtonView(),
                ephemeral=True
            )
        elif custom_id == "produce":
            # Show Produce resource selection
            await interaction.response.send_message(
                "You selected **Produce**. Please choose a resource:",
                view=ProduceButtonView(),
                ephemeral=True
            )
        elif custom_id in scroop_custom_ids:
            # Show Scroop quantity selection
            await interaction.response.send_message(
                f"You selected **{custom_id.capitalize()}**. Please choose a quantity:",
                view=ScroopQuantityButtonView(custom_id),
                ephemeral=True
            )
        elif custom_id in scroop_quantity_custom_ids:
            await interaction.response.send_message(
                f"You selected **{custom_id}**. Choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        elif custom_id in refine_custom_ids:
            await interaction.response.send_message(
                f"You selected **{custom_id.capitalize()}**. Please choose a quantity:",
                view=RefineQuantityButtonView(custom_id),
                ephemeral=True
            )
        elif custom_id in refine_quantity_custom_ids:
            await interaction.response.send_message(
                f"You selected **{custom_id}**. Choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        elif custom_id in produce_custom_ids:
            view_mapping = {
                "produce_small_arms": SmallArmsButtonView,
                "produce_heavy_arms": HeavyArmsButtonView,
                "produce_heavy_ammunition": HeavyAmmunitionButtonView,
                "produce_utility": UtilityButtonView,
                "produce_resource": ResourceButtonView,
                "produce_medical": MedicalButtonView,
                "produce_uniforms": UniformsButtonView,
                "produce_vehicles": VehiclesButtonView,
                "produce_shippable_structure": ShippableStructureButtonView
            }
            view_class = view_mapping.get(custom_id)
            if view_class:
                await interaction.response.send_message(
                    f"You selected **{custom_id.capitalize()}**. Choose a quantity:",
                    view=view_class(),
                    ephemeral=True
                )
        elif custom_id in (
            small_arms_custom_ids + heavy_arms_custom_ids + heavy_ammunition_custom_ids +
            utility_custom_ids + resource_custom_ids + medical_custom_ids + uniforms_custom_ids
        ):
            await interaction.response.send_message(
                f"You selected **{custom_id}**. Choose a quantity:",
                view=CrateQuantityButtonView(custom_id),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "This feature is not implemented yet. Please check back later.",
                ephemeral=True
            )

# Setup function for adding the cog
async def setup(bot):
    await bot.add_cog(TaskDashboardCog(bot))