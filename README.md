# KasaControl
Control Kasa RGB Light Bulbs Using Python

# Instructions for Using `KasaControl.py`

The `KasaControl.py` script allows you to control your Kasa smart devices by applying presets or changing individual light colors directly via the command line.

## Prerequisites

1. **Required Files**:
   - `Colors.csv`: A file mapping color names to RGB values.
   - `presets.json`: A file defining presets with light names and their associated colors.

2. **Install Dependencies**:
   Make sure to install the `python-kasa` library:
   ```bash
   pip install python-kasa
   ```

3. **Ensure Network Connectivity**:
   All Kasa devices must be on the same network as the computer running the script.

---

## Usage

### General Syntax
Run the script using the following syntax:
```bash
python KasaControl.py <command> <arguments>
```

### Commands

#### 1. **Apply a Preset**
To apply a preset to your lights:
```bash
python KasaControl.py preset <preset_name>
```
- Replace `<preset_name>` with the name of the preset defined in `presets.json`.

**Example**:
```bash
python KasaControl.py preset Thanksgiving
```

---

#### 2. **Change a Light’s Color**
To change the color of a specific light:
```bash
python KasaControl.py light <light_name> <color>
```
- Replace `<light_name>` with the alias of the light (as discovered on the network).
- Replace `<color>` with either:
  - A color name (defined in `Colors.csv`).
  - An RGB value in the format `[R,G,B]`.

**Examples**:
- Using a color name:
  ```bash
  python KasaControl.py light "Front Porch" Warm White
  ```
- Using RGB values:
  ```bash
  python KasaControl.py light "Front Porch" [255,140,0]
  ```

---

## File Formats

### `Colors.csv`
The `Colors.csv` file maps color names to RGB values. Example:
```csv
Name,Red,Green,Blue
Warm White,255,223,196
Red,255,0,0
Green,0,255,0
Blue,0,0,255
Orange,255,165,0
```

### `presets.json`
The `presets.json` file defines presets with light names and their respective colors. Example:
```json
{
    "Thanksgiving": [
        {"name": "Front Porch", "color": [255, 140, 0]},
        {"name": "Garage Left", "color": [255, 69, 0]},
        {"name": "Garage Center", "color": [255, 140, 0]},
        {"name": "Garage Right", "color": [255, 69, 0]}
    ],
    "Warm White": [
        {"name": "Front Porch", "color": "Warm White"},
        {"name": "Garage Left", "color": "Warm White"},
        {"name": "Garage Center", "color": "Warm White"},
        {"name": "Garage Right", "color": "Warm White"}
    ]
}
```

---

## Notes

1. **Device Discovery**:
   - The script automatically discovers devices on the network, so ensure all devices are connected and powered on.

2. **Error Handling**:
   - If a device is unresponsive or not found, the script will print an appropriate message.

3. **Switch Control**:
   - The script ensures that any controlling switch is turned on before attempting to change light colors.

---

## Example Workflow

1. Apply a preset to all lights:
   ```bash
   python KasaControl.py preset Thanksgiving
   ```

2. Change the color of a specific light:
   ```bash
   python KasaControl.py light "Front Porch" [255,140,0]
   ```

3. Change the color using a name defined in `Colors.csv`:
   ```bash
   python KasaControl.py light "Front Porch" Warm White
   ```

For additional help or troubleshooting, check the printed output of the script.
