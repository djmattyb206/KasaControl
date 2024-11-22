import asyncio
import json
import csv
import os
import sys
from kasa import Discover
from kasa.iot import IotPlug

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# File paths
colors_file = os.path.join(script_dir, "Colors.csv")
presets_file = os.path.join(script_dir, "presets.json")

# Load colors from Colors.csv into a dictionary
def load_colors():
    color_dict = {}
    with open(colors_file, mode="r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            name = row[0].strip()
            rgb = tuple(map(int, row[1:4]))  # Convert RGB values to a tuple of integers
            color_dict[name] = rgb
    return color_dict

# Load presets from presets.json
def load_presets():
    with open(presets_file, mode="r") as file:
        presets = json.load(file)
    return presets

# Cache discovered devices for efficiency
_discovered_devices = None

async def discover_devices():
    """Discover all devices on the network and cache the results."""
    global _discovered_devices
    if _discovered_devices is None:
        print("Discovering devices on the network...")
        _discovered_devices = await Discover.discover()
    return _discovered_devices

async def get_device_info_by_alias(alias):
    """Find device information by its alias."""
    devices = await discover_devices()
    for _, dev in devices.items():
        if dev.alias.lower() == alias.lower():
            return dev
    return None

async def ensure_switch_is_on():
    """Ensures the smart switch controlling the bulbs is on using its alias."""
    switch_alias = "Outside Front Lights"  # Replace with the alias of your switch
    switch_device = await get_device_info_by_alias(switch_alias)
    
    if not switch_device:
        print(f"Unable to find the switch with alias '{switch_alias}'.")
        return

    switch = IotPlug(switch_device.host)
    await switch.update()
    
    if not switch.is_on:
        print("Switch is off; turning it on to power the bulbs.")
        await switch.turn_on()
        await asyncio.sleep(5)  # Wait 5 seconds for the bulbs to power up
    else:
        print("Switch is on. Setting colors...")

async def control_bulb(alias, color_input, color_dict):
    """Control a bulb by its alias and set its color."""
    red, green, blue = get_rgb_value(color_input, color_dict)  # Get RGB from name or tuple

    try:
        bulb_device = await get_device_info_by_alias(alias)
        if not bulb_device:
            print(f"{alias}: Unable to find device.")
            return

        bulb = await Discover.discover_single(bulb_device.host)
        await bulb.update()
        await bulb.turn_on()  # Turn the bulb on before setting color

        # Convert RGB to HSV
        hue, saturation, value = rgb_to_hsv(red, green, blue)
        hue, saturation, value = int(hue), int(saturation), int(value)

        # Check for light module in available modules and set color
        light_module = next((module for module in bulb.modules.values() if hasattr(module, "set_hsv")), None)

        if light_module:
            await light_module.set_hsv(hue, saturation, value)
        elif hasattr(bulb, "set_hue") and hasattr(bulb, "set_brightness"):
            await bulb.set_hue(hue)
            await bulb.set_brightness(value)
        elif hasattr(bulb, "set_color_temp"):
            await bulb.set_color_temp(4000)
        else:
            print(f"{alias}: No suitable color control methods available.")
            return

        # Print color preview with blocks
        print(f"{alias}: Color changed to RGB ({red}, {green}, {blue}) \033[48;2;{red};{green};{blue}m    \033[0m.")

    except Exception as e:
        print(f"{alias}: Bulb unresponsive. Checking the power switch.")
        await ensure_switch_is_on()

async def set_preset(preset_name, color_dict, presets):
    """Apply a preset by setting colors for all bulbs defined in the preset."""
    bulbs = presets.get(preset_name)
    if bulbs:
        await ensure_switch_is_on()
        for bulb in bulbs:
            await control_bulb(bulb["name"], bulb["color"], color_dict)
        print(f"Preset '{preset_name}' applied successfully.")
    else:
        print(f"Preset '{preset_name}' not found.")

async def change_light_color(light_name, color, color_dict):
    """Change the color of a specific light."""
    await ensure_switch_is_on()
    await control_bulb(light_name, color, color_dict)

def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    maxc = max(r, g, b)
    minc = min(r, g, b)
    v = maxc * 100
    if minc == maxc:
        return 0.0, 0.0, v
    s = (maxc - minc) / maxc * 100
    rc = (maxc - r) / (maxc - minc)
    gc = (maxc - g) / (maxc - minc)
    bc = (maxc - b) / (maxc - minc)
    if r == maxc:
        h = bc - gc
    elif g == maxc:
        h = 2.0 + rc - bc
    else:
        h = 4.0 + gc - rc
    h = (h / 6.0) % 1.0
    return h * 360, s, v

def get_rgb_value(color_input, color_dict):
    if isinstance(color_input, str):  # Check if it's a color name
        return color_dict.get(color_input, (255, 255, 255))  # Default to white if not found
    elif isinstance(color_input, list) and len(color_input) == 3:  # Direct RGB list
        return tuple(color_input)  # Convert list to tuple
    else:
        raise ValueError("Invalid color input. Must be a color name or RGB tuple.")

if __name__ == "__main__":
    # Load colors and presets
    color_dict = load_colors()
    presets = load_presets()

    # Parse command-line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "preset" and len(sys.argv) > 2:
            # Apply a preset
            preset_name = sys.argv[2]
            asyncio.run(set_preset(preset_name, color_dict, presets))
        elif command == "light" and len(sys.argv) > 3:
            # Change an individual light's color
            light_name = sys.argv[2]
            color = sys.argv[3]

            # Parse color as RGB if it's in a list format
            if color.startswith("[") and color.endswith("]"):
                color = list(map(int, color.strip("[]").split(",")))
            asyncio.run(change_light_color(light_name, color, color_dict))
        else:
            print("Usage:")
            print("  python KasaControl.py preset <preset_name>")
            print("  python KasaControl.py light <light_name> <color_name_or_rgb>")
    else:
        print("Usage:")
        print("  python KasaControl.py preset <preset_name>")
        print("  python KasaControl.py light <light_name> <color_name_or_rgb>")
