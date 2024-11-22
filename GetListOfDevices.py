import asyncio
from kasa import Discover
import pandas as pd
import os

# Mapping for models, types, and details
model_info = {
    "HS210(US)": {"Type": "Switch", "Detail": "3 Way"},
    "HS200(US)": {"Type": "Switch", "Detail": "Standard"},
    "KL130(US)": {"Type": "Bulb", "Detail": "Multicolor"},
    "HS220(US)": {"Type": "Switch", "Detail": "Dimmer"},
    "KP115(US)": {"Type": "Plug", "Detail": "With Energy Monitoring"},
    "HS103(US)": {"Type": "Plug", "Detail": "Lite"},
    "HS105(US)": {"Type": "Plug", "Detail": "Mini"},
    "KP400(US)": {"Type": "Plug", "Detail": "Outdoor"},
    "KP405(US)": {"Type": "Plug", "Detail": "Outdoor Dimmer"},
    "EP40(US)": {"Type": "Plug", "Detail": "Outdoor"},
}

async def discover_devices_and_save_to_script_folder():
    devices = await Discover.discover()

    # Prepare the data for saving
    data = []
    for addr, dev in devices.items():
        model_details = model_info.get(dev.model, {"Type": "", "Detail": ""})
        data.append({
            "IP": addr,
            "Alias": dev.alias,
            "MAC": dev.mac,
            "Model": dev.model,
            "Type": model_details["Type"],
            "Detail": model_details["Detail"]
        })

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Determine the script folder and save the file there
    script_folder = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_folder, "Devices_with_Type_and_Detail.xlsx")

    # Save to Excel
    df.to_excel(file_path, index=False)
    print(f"Saved discovered devices to {file_path}")

# Run the async function
asyncio.run(discover_devices_and_save_to_script_folder())
