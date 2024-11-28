import discord
from discord.ext import commands
from discord.ui import Button, View
import logging

# Add this at the beginning of your file to configure logging
logging.basicConfig(level=logging.INFO)

# Create a dashboard view
class DashboardView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Make the view persistent (no timeout)
        self.add_item(Button(label="Scroop", style=discord.ButtonStyle.green, custom_id="scroop"))
        self.add_item(Button(label="Refine", style=discord.ButtonStyle.green, custom_id="refine"))
        self.add_item(Button(label="Produce", style=discord.ButtonStyle.green, custom_id="produce"))
        self.add_item(Button(label="Transport", style=discord.ButtonStyle.green, custom_id="transport"))

# Buttons for Scroop selection
class ScroopButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        self.add_item(Button(label="Salvage", style=discord.ButtonStyle.green, custom_id="salvage"))
        self.add_item(Button(label="Components", style=discord.ButtonStyle.green, custom_id="components"))
        self.add_item(Button(label="Sulfur", style=discord.ButtonStyle.green, custom_id="sulfur"))
        self.add_item(Button(label="Coal", style=discord.ButtonStyle.green, custom_id="coal"))
        
# Buttons for Scroop resource quantity selection, will also be used for refine quantity selection to save time
class ScroopQuantityButtonView(View):
    def __init__(self, resource):
        super().__init__(timeout=None)  # Persistent view
        self.resource = resource  # Pass resource type for context
        self.add_item(Button(label="1500", style=discord.ButtonStyle.green, custom_id=f"{resource}scroop_1500"))
        self.add_item(Button(label="2500", style=discord.ButtonStyle.green, custom_id=f"{resource}scroop_2500"))
        self.add_item(Button(label="5000", style=discord.ButtonStyle.green, custom_id=f"{resource}scroop_5000"))
        
# sub category selection for when a user selects produce, (Small Arms, Heavy Arms, Heavy Ammunition, Utility, Medical, Resource, Uniforms, Vehicles, Shippable Structure)
class ProduceButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        self.add_item(Button(label="Small Arms", style=discord.ButtonStyle.green, custom_id="produce_small_arms"))
        self.add_item(Button(label="Heavy Arms", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms"))
        self.add_item(Button(label="Heavy Ammunition", style=discord.ButtonStyle.green, custom_id="produce_heavy_ammunition"))
        self.add_item(Button(label="Utility", style=discord.ButtonStyle.green, custom_id="produce_utility"))
        self.add_item(Button(label="Resource", style=discord.ButtonStyle.green, custom_id="produce_resource"))
        self.add_item(Button(label="Medical", style=discord.ButtonStyle.green, custom_id="produce_medical"))        
        self.add_item(Button(label="Uniforms", style=discord.ButtonStyle.green, custom_id="produce_uniforms"))
        self.add_item(Button(label="Vehicles", style=discord.ButtonStyle.green, custom_id="produce_vehicles"))
        self.add_item(Button(label="Shippable Structure", style=discord.ButtonStyle.green, custom_id="produce_shippable_structure"))
        
# Sub category for Small arms item buttons (dusk ce.iii, 7.92mm, catara mo.ii, krn886-127 gast machine gun, bomastone granade, 8mm, Cometa t2-9, .44, catena rt.iv autorifle, argenti r.ii rifle, volta r.i repeater, fuscina pi.i, krr2-790 omen, krr3-792 auger, 7.62, krd1-750 dragonfly, buckshot, the pitch gun mc.v, lionclaw mc.viii, 9mm, pt-815 smoke granade, green ash grenade, 12.7mm)
class SmallArmsButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Dusk CE.III", style=discord.ButtonStyle.green, custom_id="produce_small_arms_dusk_ce_iii"))
        self.add_item(Button(label="7.92mm", style=discord.ButtonStyle.green, custom_id="produce_small_arms_792mm"))
        self.add_item(Button(label="Catara MO.II", style=discord.ButtonStyle.green, custom_id="produce_small_arms_catara_mo_ii"))
        self.add_item(Button(label="KRN886-127 Gast Machine Gun", style=discord.ButtonStyle.green, custom_id="produce_small_arms_krn886_127_gast_machine_gun"))
        self.add_item(Button(label="Bomastone Granade", style=discord.ButtonStyle.green, custom_id="produce_small_arms_bomastone_granade"))
        self.add_item(Button(label="8mm", style=discord.ButtonStyle.green, custom_id="produce_small_arms_8mm"))
        self.add_item(Button(label="Cometa T2-9", style=discord.ButtonStyle.green, custom_id="produce_small_arms_cometa_t2_9"))
        self.add_item(Button(label=".44", style=discord.ButtonStyle.green, custom_id="produce_small_arms_44"))
        self.add_item(Button(label="Catena RT.IV Autorifle", style=discord.ButtonStyle.green, custom_id="produce_small_arms_catena_rt_iv_autorifle"))
        self.add_item(Button(label="Argenti R.II Rifle", style=discord.ButtonStyle.green, custom_id="produce_small_arms_argenti_r_ii_rifle"))
        self.add_item(Button(label="Volta R.I Repeater", style=discord.ButtonStyle.green, custom_id="produce_small_arms_volta_r_i_repeater"))
        self.add_item(Button(label="Fuscina PI.I", style=discord.ButtonStyle.green, custom_id="produce_small_arms_fuscina_pi_i"))
        self.add_item(Button(label="KRR2-790 Omen", style=discord.ButtonStyle.green, custom_id="produce_small_arms_krr2_790_omen"))
        self.add_item(Button(label="KRR3-792 Auger", style=discord.ButtonStyle.green, custom_id="produce_small_arms_krr3_792_auger"))
        self.add_item(Button(label="7.62", style=discord.ButtonStyle.green, custom_id="produce_small_arms_762"))
        self.add_item(Button(label="KRD1-750 Dragonfly", style=discord.ButtonStyle.green, custom_id="produce_small_arms_krd1_750_dragonfly"))
        self.add_item(Button(label="Buckshot", style=discord.ButtonStyle.green, custom_id="produce_small_arms_buckshot"))
        self.add_item(Button(label="The Pitch Gun MC.V", style=discord.ButtonStyle.green, custom_id="produce_small_arms_the_pitch_gun_mc_v"))
        self.add_item(Button(label="Lionclaw MC.VIII", style=discord.ButtonStyle.green, custom_id="produce_small_arms_lionclaw_mc_viii"))
        self.add_item(Button(label="9mm", style=discord.ButtonStyle.green, custom_id="produce_small_arms_9mm"))
        self.add_item(Button(label="PT-815 Smoke Granade", style=discord.ButtonStyle.green, custom_id="produce_small_arms_pt_815_smoke_granade"))
        self.add_item(Button(label="Green Ash Grenade", style=discord.ButtonStyle.green, custom_id="produce_small_arms_green_ash_grenade"))
        self.add_item(Button(label="12.7mm", style=discord.ButtonStyle.green, custom_id="produce_small_arms_127mm"))
        
# Sub category for Heavy arms item buttons (typhon ra.xii, 20mm, venom c.iii 35, bane 45, ap/rpg, arc/rpg, molten wind v.11 flame torch, klg901-2 lunair f, mounted fissura gd.i, tremola grenade gpb-1, lamentum mm.iv, daucus isg.iii, 30mm, cremari mortar, flare mortar shell, shrapnel mortar sheel, mortar sheel, ignifist 30, mammon 91-b, anti-tank sticky bomb, rpg)
class HeavyArmsButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Typhon RA.XII", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_typhon_ra_xii"))
        self.add_item(Button(label="20mm", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_20mm"))
        self.add_item(Button(label="Venom C.III 35", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_venom_c_iii_35"))
        self.add_item(Button(label="Bane 45", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_bane_45"))
        self.add_item(Button(label="AP/RPG", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_ap_rpg"))
        self.add_item(Button(label="ARC/RPG", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_arc_rpg"))
        self.add_item(Button(label="Molten Wind V.11 Flame Torch", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_molten_wind_v_11_flame_torch"))
        self.add_item(Button(label="KLG901-2 Lunair F", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_klg901_2_lunair_f"))
        self.add_item(Button(label="Mounted Fissura GD.I", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_mounted_fissura_gd_i"))
        self.add_item(Button(label="Tremola Grenade GPB-1", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_tremola_grenade_gpb_1"))
        self.add_item(Button(label="Lamentum MM.IV", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_lamentum_mm_iv"))
        self.add_item(Button(label="Daucus ISG.III", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_daucus_isg_iii"))
        self.add_item(Button(label="30mm", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_30mm"))
        self.add_item(Button(label="Cremari Mortar", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_cremari_mortar"))
        self.add_item(Button(label="Flare Mortar Shell", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_flare_mortar_shell"))
        self.add_item(Button(label="Shrapnel Mortar Shell", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_shrapnel_mortar_shell"))
        self.add_item(Button(label="Mortar Shell", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_mortar_shell"))
        self.add_item(Button(label="Ignifist 30", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_ignifist_30"))
        self.add_item(Button(label="Mammon 91-B", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_mammon_91_b"))
        self.add_item(Button(label="Anti-Tank Sticky Bomb", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_anti_tank_sticky_bomb"))
        self.add_item(Button(label="RPG", style=discord.ButtonStyle.green, custom_id="produce_heavy_arms_rpg"))
        
# Sub category for Heavy Ammunition item buttons (150mm, 120mm, 250mm, 68mm, 40mm)
class HeavyAmmunitionButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="150mm", style=discord.ButtonStyle.green, custom_id="produce_heavy_ammunition_150mm"))
        self.add_item(Button(label="120mm", style=discord.ButtonStyle.green, custom_id="produce_heavy_ammunition_120mm"))
        self.add_item(Button(label="250mm", style=discord.ButtonStyle.green, custom_id="produce_heavy_ammunition_250mm"))
        self.add_item(Button(label="68mm", style=discord.ButtonStyle.green, custom_id="produce_heavy_ammunition_68mm"))
        self.add_item(Button(label="40mm", style=discord.ButtonStyle.green, custom_id="produce_heavy_ammunition_40mm"))
        
# Sub category for Utility item buttons (barbed wire, buckhorn ccq-18, binoculars, hydra's whisper, havoc charge, molten wind v.ii ammo, listening kit, metal beam, radio backpack, sandbag, havoc charge denotator, shovel, sledge hammer, tripod, wind stock, wrench, water bucket, gas mansk, gas mask filter, radio)
class UtilityButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Barbed Wire", style=discord.ButtonStyle.green, custom_id="produce_utility_barbed_wire"))
        self.add_item(Button(label="Buckhorn CCQ-18", style=discord.ButtonStyle.green, custom_id="produce_utility_buckhorn_ccq_18"))
        self.add_item(Button(label="Binoculars", style=discord.ButtonStyle.green, custom_id="produce_utility_binoculars"))
        self.add_item(Button(label="Hydra's Whisper", style=discord.ButtonStyle.green, custom_id="produce_utility_hydras_whisper"))
        self.add_item(Button(label="Havoc Charge", style=discord.ButtonStyle.green, custom_id="produce_utility_havoc_charge"))
        self.add_item(Button(label="Molten Wind V.II Ammo", style=discord.ButtonStyle.green, custom_id="produce_utility_molten_wind_v_ii_ammo"))
        self.add_item(Button(label="Listening Kit", style=discord.ButtonStyle.green, custom_id="produce_utility_listening_kit"))
        self.add_item(Button(label="Metal Beam", style=discord.ButtonStyle.green, custom_id="produce_utility_metal_beam"))
        self.add_item(Button(label="Radio Backpack", style=discord.ButtonStyle.green, custom_id="produce_utility_radio_backpack"))
        self.add_item(Button(label="Sandbag", style=discord.ButtonStyle.green, custom_id="produce_utility_sandbag"))
        self.add_item(Button(label="Havoc Charge Denotator", style=discord.ButtonStyle.green, custom_id="produce_utility_havoc_charge_denotator"))
        self.add_item(Button(label="Shovel", style=discord.ButtonStyle.green, custom_id="produce_utility_shovel"))
        self.add_item(Button(label="Sledge Hammer", style=discord.ButtonStyle.green, custom_id="produce_utility_sledge_hammer"))
        self.add_item(Button(label="Tripod", style=discord.ButtonStyle.green, custom_id="produce_utility_tripod"))
        self.add_item(Button(label="Wind Stock", style=discord.ButtonStyle.green, custom_id="produce_utility_wind_stock"))
        self.add_item(Button(label="Wrench", style=discord.ButtonStyle.green, custom_id="produce_utility_wrench"))
        self.add_item(Button(label="Water Bucket", style=discord.ButtonStyle.green, custom_id="produce_utility_water_bucket"))
        self.add_item(Button(label="Gas Mask", style=discord.ButtonStyle.green, custom_id="produce_utility_gas_mask"))
        self.add_item(Button(label="Gas Mask Filter", style=discord.ButtonStyle.green, custom_id="produce_utility_gas_mask_filter"))
        self.add_item(Button(label="Radio", style=discord.ButtonStyle.green, custom_id="produce_utility_radio"))
        
# Sub category for Resource item buttons (maintenance supplies)
class ResourceButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Maintenance Supplies", style=discord.ButtonStyle.green, custom_id="produce_resource_maintenance_supplies"))
        
# Sub category for Medical item buttons (bandage, first aid kit, trauma kit, blood plasma, soldier supplies)
class MedicalButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Bandage", style=discord.ButtonStyle.green, custom_id="produce_medical_bandage"))
        self.add_item(Button(label="First Aid Kit", style=discord.ButtonStyle.green, custom_id="produce_medical_first_aid_kit"))
        self.add_item(Button(label="Trauma Kit", style=discord.ButtonStyle.green, custom_id="produce_medical_trauma_kit"))
        self.add_item(Button(label="Blood Plasma", style=discord.ButtonStyle.green, custom_id="produce_medical_blood_plasma"))
        self.add_item(Button(label="Soldier Supplies", style=discord.ButtonStyle.green, custom_id="produce_medical_soldier_supplies"))
        
# Sub category for Uniforms item buttons (vilian flak vest, fabri rucksack, grenadier's baldric, medic fatigues, officialis attire, legionary's oilcoat, recon camo, heavy topcoat, tankman's coveralls)
class UniformsButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Vilian Flak Vest", style=discord.ButtonStyle.green, custom_id="produce_uniforms_vilian_flak_vest"))
        self.add_item(Button(label="Fabri Rucksack", style=discord.ButtonStyle.green, custom_id="produce_uniforms_fabri_rucksack"))
        self.add_item(Button(label="Grenadier's Baldric", style=discord.ButtonStyle.green, custom_id="produce_uniforms_grenadiers_baldric"))
        self.add_item(Button(label="Medic Fatigues", style=discord.ButtonStyle.green, custom_id="produce_uniforms_medic_fatigues"))
        self.add_item(Button(label="Officialis Attire", style=discord.ButtonStyle.green, custom_id="produce_uniforms_officialis_attire"))
        self.add_item(Button(label="Legionary's Oilcoat", style=discord.ButtonStyle.green, custom_id="produce_uniforms_legionarys_oilcoat"))
        self.add_item(Button(label="Recon Camo", style=discord.ButtonStyle.green, custom_id="produce_uniforms_recon_camo"))
        self.add_item(Button(label="Heavy Topcoat", style=discord.ButtonStyle.green, custom_id="produce_uniforms_heavy_topcoat"))
        self.add_item(Button(label="Tankman's Coveralls", style=discord.ButtonStyle.green, custom_id="produce_uniforms_tankmans_coveralls"))
        
# Sub category for Vehicles item buttons (r-12- salus ambulance, t3 xiphos, r-15- chariot, aa-2 battering ram, g40 sagittarii, bms - packmule flatbed, hh-a javelin, ab-8 acheron, 120-68 koronides field gun, hc-2 scorpion, h-5 hatchet, 86k-a bardiche, 90t-v nemesis, 85k-b falchion, 03mm caster, r-5 atlas hauler, rr-3 stolon tanker, r-1 hauler, t12 actaeon tankette, uv-05a argonaut, roster 0 junkwagon)
class VehiclesButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="R-12- Salus Ambulance", style=discord.ButtonStyle.green, custom_id="produce_vehicles_r_12_salus_ambulance"))
        self.add_item(Button(label="T3 Xiphos", style=discord.ButtonStyle.green, custom_id="produce_vehicles_t3_xiphos"))
        self.add_item(Button(label="R-15- Chariot", style=discord.ButtonStyle.green, custom_id="produce_vehicles_r_15_chariot"))
        self.add_item(Button(label="AA-2 Battering Ram", style=discord.ButtonStyle.green, custom_id="produce_vehicles_aa_2_battering_ram"))
        self.add_item(Button(label="G40 Sagittarii", style=discord.ButtonStyle.green, custom_id="produce_vehicles_g40_sagittarii"))
        self.add_item(Button(label="BMS - Packmule Flatbed", style=discord.ButtonStyle.green, custom_id="produce_vehicles_bms_packmule_flatbed"))
        self.add_item(Button(label="HH-A Javelin", style=discord.ButtonStyle.green, custom_id="produce_vehicles_hh_a_javelin"))
        self.add_item(Button(label="AB-8 Acheron", style=discord.ButtonStyle.green, custom_id="produce_vehicles_ab_8_acheron"))
        self.add_item(Button(label="120-68 Koronides Field Gun", style=discord.ButtonStyle.green, custom_id="produce_vehicles_120_68_koronides_field_gun"))
        self.add_item(Button(label="HC-2 Scorpion", style=discord.ButtonStyle.green, custom_id="produce_vehicles_hc_2_scorpion"))
        self.add_item(Button(label="H-5 Hatchet", style=discord.ButtonStyle.green, custom_id="produce_vehicles_h_5_hatchet"))
        self.add_item(Button(label="86K-A Bardiche", style=discord.ButtonStyle.green, custom_id="produce_vehicles_86k_a_bardiche"))
        self.add_item(Button(label="90T-V Nemesis", style=discord.ButtonStyle.green, custom_id="produce_vehicles_90t_v_nemesis"))
        self.add_item(Button(label="85K-B Falchion", style=discord.ButtonStyle.green, custom_id="produce_vehicles_85k_b_falchion"))
        self.add_item(Button(label="03MM Caster", style=discord.ButtonStyle.green, custom_id="produce_vehicles_03mm_caster"))
        self.add_item(Button(label="R-5 Atlas Hauler", style=discord.ButtonStyle.green, custom_id="produce_vehicles_r_5_atlas_hauler"))
        self.add_item(Button(label="RR-3 Stolon Tanker", style=discord.ButtonStyle.green, custom_id="produce_vehicles_rr_3_stolon_tanker"))
        self.add_item(Button(label="R-1 Hauler", style=discord.ButtonStyle.green, custom_id="produce_vehicles_r_1_hauler"))
        self.add_item(Button(label="T12 Actaeon Tankette", style=discord.ButtonStyle.green, custom_id="produce_vehicles_t12_actaeon_tankette"))
        self.add_item(Button(label="UV-05A Argonaut", style=discord.ButtonStyle.green, custom_id="produce_vehicles_uv_05a_argonaut"))
        self.add_item(Button(label="Roster 0 Junkwagon", style=discord.ButtonStyle.green, custom_id="produce_vehicles_roster_0_junkwagon"))
        
# Sub category for Shippable structure (50-500 thunderbolt cannon, material pallet, resource container, shipping container, dae 1o-3 polybolos, concrete mixer, liquid container) 
class ShippableStructureButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="50-500 Thunderbolt Cannon", style=discord.ButtonStyle.green, custom_id="produce_shippable_structure_50_500_thunderbolt_cannon"))
        self.add_item(Button(label="Material Pallet", style=discord.ButtonStyle.green, custom_id="produce_shippable_structure_material_pallet"))
        self.add_item(Button(label="Resource Container", style=discord.ButtonStyle.green, custom_id="produce_shippable_structure_resource_container"))
        self.add_item(Button(label="Shipping Container", style=discord.ButtonStyle.green, custom_id="produce_shippable_structure_shipping_container"))
        self.add_item(Button(label="DAE 1O-3 Polybolos", style=discord.ButtonStyle.green, custom_id="produce_shippable_structure_dae_1o_3_polybolos"))
        self.add_item(Button(label="Concrete Mixer", style=discord.ButtonStyle.green, custom_id="produce_shippable_structure_concrete_mixer"))
        self.add_item(Button(label="Liquid Container", style=discord.ButtonStyle.green, custom_id="produce_shippable_structure_liquid_container"))                  

# crate quantity selesction, 10, 20, 30, 40, 50
class CrateQuantityButtonView(View):
    def __init__(self, resource):
        super().__init__(timeout=None)  # Persistent view
        self.resource = resource  # Pass resource type for context
        self.add_item(Button(label="10", style=discord.ButtonStyle.green, custom_id=f"{resource}produce_crate_10"))
        self.add_item(Button(label="20", style=discord.ButtonStyle.green, custom_id=f"{resource}produce_crate_20"))
        self.add_item(Button(label="30", style=discord.ButtonStyle.green, custom_id=f"{resource}produce_crate_30"))
        self.add_item(Button(label="40", style=discord.ButtonStyle.green, custom_id=f"{resource}produce_crate_40"))
        self.add_item(Button(label="50", style=discord.ButtonStyle.green, custom_id=f"{resource}produce_crate_50"))
        
# Buttons for Refine options
class RefineButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        self.add_item(Button(label="Basic Materials", style=discord.ButtonStyle.green, custom_id="refine_basic_materials"))
        self.add_item(Button(label="Diesel", style=discord.ButtonStyle.green, custom_id="refine_diesel"))
        self.add_item(Button(label="Explosive Powder", style=discord.ButtonStyle.green, custom_id="refine_explosive_powder"))
        self.add_item(Button(label="Refined Materials", style=discord.ButtonStyle.green, custom_id="refine_refined_materials"))
        self.add_item(Button(label="Heavy Explosive Powder", style=discord.ButtonStyle.green, custom_id="refine_heavy_explosive_powder"))
        self.add_item(Button(label="Gravel", style=discord.ButtonStyle.green, custom_id="refine_gravel"))
        
# Buttons for delivery options
class DeliveryButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        self.add_item(Button(label="Backline Stockpile", style=discord.ButtonStyle.green, custom_id="delivery_backline"))
        self.add_item(Button(label="Midline Stockpile", style=discord.ButtonStyle.green, custom_id="delivery_midline"))
        self.add_item(Button(label="Frontline", style=discord.ButtonStyle.green, custom_id="delivery_frontline"))
        self.add_item(Button(label="Other", style=discord.ButtonStyle.green, custom_id="delivery_other"))

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
        # elif for scroop resource selection
        elif custom_id == "salvage":
            await interaction.response.send_message(
                "You selected **Salvage**. Please choose a quantity:",
                view=ScroopQuantityButtonView("salvage"),
                ephemeral=True
            )
        # after selecting salvage quantity, the user will be able to select a delivery location
        elif custom_id == "salvagescroop_1500":
            await interaction.response.send_message(
                "You selected **1500 Salvage**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 2500 salvage
        elif custom_id == "salvagescroop_2500":
            await interaction.response.send_message(
                "You selected **2500 Salvage**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 5000 salvage
        elif custom_id == "salvagescroop_5000":
            await interaction.response.send_message(
                "You selected **5000 Salvage**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        elif custom_id == "components":
            await interaction.response.send_message(
                "You selected **Components**. Please choose a quantity:",
                view=ScroopQuantityButtonView("components"),
                ephemeral=True
            )
        # after selecting components quantity, the user will be able to select a delivery location
        elif custom_id == "componentsscroop_1500":
            await interaction.response.send_message(
                "You selected **1500 Components**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 2500 components
        elif custom_id == "componentsscroop_2500":
            await interaction.response.send_message(
                "You selected **2500 Components**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 5000 components
        elif custom_id == "componentsscroop_5000":
            await interaction.response.send_message(
                "You selected **5000 Components**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        elif custom_id == "sulfur":
            await interaction.response.send_message(
                "You selected **Sulfur**. Please choose a quantity:",
                view=ScroopQuantityButtonView("sulfur"),
                ephemeral=True
            )
        # after selecting sulfur quantity, the user will be able to select a delivery location
        elif custom_id == "sulfurscroop_1500":
            await interaction.response.send_message(
                "You selected **1500 Sulfur**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 2500 sulfur
        elif custom_id == "sulfurscroop_2500":
            await interaction.response.send_message(
                "You selected **2500 Sulfur**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 5000 sulfur
        elif custom_id == "sulfurscroop_5000":
            await interaction.response.send_message(
                "You selected **5000 Sulfur**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        elif custom_id == "coal":
            await interaction.response.send_message(
                "You selected **Coal**. Please choose a quantity:",
                view=ScroopQuantityButtonView("coal"),
                ephemeral=True
            )
        # after selecting coal quantity, the user will be able to select a delivery location
        elif custom_id == "coalscroop_1500":
            await interaction.response.send_message(
                "You selected **1500 Coal**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 2500 coal
        elif custom_id == "coalscroop_2500":
            await interaction.response.send_message(
                "You selected **2500 Coal**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 5000 coal
        elif custom_id == "coalscroop_5000":
            await interaction.response.send_message(
                "You selected **5000 Coal**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        
        # elif for refine selection
        elif custom_id == "refine":
            # Show refine resource selection
            await interaction.response.send_message(
                "You selected **Refine**. Please choose a resource:",
                view=RefineButtonView(),
                ephemeral=True
            )
        # handle case for basic materials
        elif custom_id == "refine_basic_materials":
            await interaction.response.send_message(
                "You selected **Basic Materials**. Please choose a quantity:",
                view=ScroopQuantityButtonView("basic_materials"),
                ephemeral=True
            )
        # after selecting basic materials quantity, the user will be able to select a delivery location
        elif custom_id == "basic_materialsscroop_1500":
            await interaction.response.send_message(
                "You selected **1500 Basic Materials**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 2500 basic materials
        elif custom_id == "basic_materialsscroop_2500":
            await interaction.response.send_message(
                "You selected **2500 Basic Materials**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 5000 basic materials
        elif custom_id == "basic_materialsscroop_5000":
            await interaction.response.send_message(
                "You selected **5000 Basic Materials**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for diesel
        elif custom_id == "refine_diesel":
            await interaction.response.send_message(
                "You selected **Diesel**. Please choose a quantity:",
                view=ScroopQuantityButtonView("diesel"),
                ephemeral=True
            )
        # after selecting diesel quantity, the user will be able to select a delivery location
        elif custom_id == "dieselscroop_1500":
            await interaction.response.send_message(
                "You selected **1500 Diesel**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 2500 diesel
        elif custom_id == "dieselscroop_2500":
            await interaction.response.send_message(
                "You selected **2500 Diesel**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 5000 diesel
        elif custom_id == "dieselscroop_5000":
            await interaction.response.send_message(
                "You selected **5000 Diesel**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for explosive powder
        elif custom_id == "refine_explosive_powder":
            await interaction.response.send_message(
                "You selected **Explosive Powder**. Please choose a quantity:",
                view=ScroopQuantityButtonView("explosive_powder"),
                ephemeral=True
            )
        # after quantity selection, the user will be able to select a delivery location
        elif custom_id == "explosive_powderscroop_1500":
            await interaction.response.send_message(
                "You selected **1500 Explosive Powder**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 2500 explosive powder
        elif custom_id == "explosive_powderscroop_2500":
            await interaction.response.send_message(
                "You selected **2500 Explosive Powder**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 5000 explosive powder
        elif custom_id == "explosive_powderscroop_5000":
            await interaction.response.send_message(
                "You selected **5000 Explosive Powder**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for refined materials
        elif custom_id == "refine_refined_materials":
            await interaction.response.send_message(
                "You selected **Refined Materials**. Please choose a quantity:",
                view=ScroopQuantityButtonView("refined_materials"),
                ephemeral=True
            )
        # after selecting refined materials quantity, the user will be able to select a delivery location
        elif custom_id == "refined_materialsscroop_1500":
            await interaction.response.send_message(
                "You selected **1500 Refined Materials**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 2500 refined materials
        elif custom_id == "refined_materialsscroop_2500":
            await interaction.response.send_message(
                "You selected **2500 Refined Materials**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 5000 refined materials
        elif custom_id == "refined_materialsscroop_5000":
            await interaction.response.send_message(
                "You selected **5000 Refined Materials**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for heavy explosive powder
        elif custom_id == "refine_heavy_explosive_powder":
            await interaction.response.send_message(
                "You selected **Heavy Explosive Powder**. Please choose a quantity:",
                view=ScroopQuantityButtonView("heavy_explosive_powder"),
                ephemeral=True
            )
        # after selecting heavy explosive powder quantity, the user will be able to select a delivery location
        elif custom_id == "heavy_explosive_powderscroop_1500":
            await interaction.response.send_message(
                "You selected **1500 Heavy Explosive Powder**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 2500 heavy
        elif custom_id == "heavy_explosive_powderscroop_2500":
            await interaction.response.send_message(
                "You selected **2500 Heavy Explosive Powder**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 5000 heavy
        elif custom_id == "heavy_explosive_powderscroop_5000":
            await interaction.response.send_message(
                "You selected **5000 Heavy Explosive Powder**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for gravel
        elif custom_id == "refine_gravel":
            await interaction.response.send_message(
                "You selected **Gravel**. Please choose a quantity:",
                view=ScroopQuantityButtonView("gravel"),
                ephemeral=True
            )
        # after selecting gravel quantity, the user will be able to select a delivery location
        elif custom_id == "gravelscroop_1500":
            await interaction.response.send_message(
                "You selected **1500 Gravel**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 2500 gravel
        elif custom_id == "gravelscroop_2500":
            await interaction.response.send_message(
                "You selected **2500 Gravel**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # handle case for 5000 gravel
        elif custom_id == "gravelscroop_5000":
            await interaction.response.send_message(
                "You selected **5000 Gravel**. Please choose a delivery location:",
                view=DeliveryButtonView(),
                ephemeral=True
            )
        # elif for produce selection
        elif custom_id == "produce":
            # Show produce category selection
            await interaction.response.send_message(
                "You selected **Produce**. Please choose a category:",
                view=ProduceButtonView(),
                ephemeral=True
            )
        # handle case for small arms selection
        elif custom_id == "produce_small_arms":
            await interaction.response.send_message(
                "You selected **Small Arms**. Please choose an item:",
                view=SmallArmsButtonView(),
                ephemeral=True
            )
        # handle case when the item Dusk CE.III is selected
        elif custom_id == "produce_small_arms_dusk_ce_iii":
            await interaction.response.send_message(
                "You selected **Dusk CE.III**. Please choose a quantity:",
                view=CrateQuantityButtonView("dusk_ce_iii"),
                ephemeral=True
            )
        # handle case for heavy arms selection
        elif custom_id == "produce_heavy_arms":
            await interaction.response.send_message(
                "You selected **Heavy Arms**. Please choose an item:",
                view=HeavyArmsButtonView(),
                ephemeral=True
            )
        # handle case for heavy ammunition selection
        elif custom_id == "produce_heavy_ammunition":
            await interaction.response.send_message(
                "You selected **Heavy Ammunition**. Please choose an item:",
                view=HeavyAmmunitionButtonView(),
                ephemeral=True
            )
        # handle case for utility selection
        elif custom_id == "produce_utility":
            await interaction.response.send_message(
                "You selected **Utility**. Please choose an item:",
                view=UtilityButtonView(),
                ephemeral=True
            )
        # handle case for resource selection
        elif custom_id == "produce_resource":
            await interaction.response.send_message(
                "You selected **Resource**. Please choose an item:",
                view=ResourceButtonView(),
                ephemeral=True
            )
        # handle case for medical selection
        elif custom_id == "produce_medical":
            await interaction.response.send_message(
                "You selected **Medical**. Please choose an item:",
                view=MedicalButtonView(),
                ephemeral=True
            )
        # handle case for uniforms selection
        elif custom_id == "produce_uniforms":
            await interaction.response.send_message(
                "You selected **Uniforms**. Please choose an item:",
                view=UniformsButtonView(),
                ephemeral=True
            )
        # handle case for vehicles selection
        elif custom_id == "produce_vehicles":
            await interaction.response.send_message(
                "You selected **Vehicles**. Please choose an item:",
                view=VehiclesButtonView(),
                ephemeral=True
            )
        # handle case for shippable structure selection
        elif custom_id == "produce_shippable_structure":
            await interaction.response.send_message(
                "You selected **Shippable Structure**. Please choose an item:",
                view=ShippableStructureButtonView(),
                ephemeral=True
            )
        else:
            print("Invalid selection")
            await interaction.response.send_message(
                "Invalid selection. Please try again.",
                ephemeral=True
            )
            
# Setup function for adding the cog
async def setup(bot):
    await bot.add_cog(TaskDashboardCog(bot))