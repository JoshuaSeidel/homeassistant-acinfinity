# AC Infinity UIS Controller Integration for Home Assistant
## AI+ Optimized Fork

> **Note**: This is an enhanced fork of the [original integration by @dalinicus](https://github.com/dalinicus/homeassistant-acinfinity), specifically optimized for **AI+ controller owners** with clearer sensor naming, comprehensive AI+ documentation, and improved user experience.

[![GitHub Release](https://img.shields.io/github/v/release/JoshuaSeidel/homeassistant-acinfinity?style=for-the-badge)](https://github.com/JoshuaSeidel/homeassistant-acinfinity/releases)
[![License](https://img.shields.io/github/license/JoshuaSeidel/homeassistant-acinfinity?style=for-the-badge)](LICENSE)

**Complete Home Assistant integration for AC Infinity UIS Controllers**. Monitor every sensor, control every port, and automate your grow environment with precision.

### 🌟 What Makes This Fork Different?

- **Crystal Clear Sensor Names** - "Tent Temperature" vs "Built-in Temperature" (no more confusion!)
- **AI+ Controller Focus** - Comprehensive docs for 8-port and 4-sensor USB controllers
- **Better Documentation** - Step-by-step guides specifically for AI+ features
- **Maintained** - Active development with focus on AI+ user experience

- [Compatibility](#compatibility)
- [What You Get](#what-you-get)
- [Installation](#installation)
- [Setup](#setup)
- [Configuration](#configuration)

**📊 AI+ Users:** See [AI_DATA_REFERENCE.md](AI_DATA_REFERENCE.md) for complete list of all 100+ data points available from your controller!

---

# Compatibility

### ✅ Supported Controllers

| Model | Ports | Sensor Ports | Notes |
|-------|-------|--------------|-------|
| **Controller AI+ (CTR89Q)** | **8** | **4 USB** | ⭐ Full featured - 8 device ports + 4 sensor ports |
| **Controller Outlet AI+ (AC-ADA8)** | **8** | **4 USB** | ⭐ Full featured - 8 outlet ports + 4 sensor ports |
| Controller Outlet AI (AC-ADA4) | 4 | 4 USB | 4 outlet ports + 4 sensor ports |
| Controller 69 Pro+ (CTR69Q) | 4 | None | 4 device ports, onboard sensors only |
| Controller 69 Pro (CTR69P) | 4 | None | 4 device ports, onboard sensors only |
| Controller 69 WiFi | 4 | None | 4 device ports, onboard sensors only |

❌ **Not Compatible**: Controller 67, Controller 69 (Bluetooth-only models without WiFi)

---

# What You Get

## For AI+ Controller Owners

Your AI+ controller gives you the complete AC Infinity experience:

### 📊 Two Sets of Climate Sensors

1. **Built-in Controller Sensors** (inside the controller unit)
   - `Built-in Temperature` - Controller's internal temperature
   - `Built-in Humidity` - Controller's internal humidity  
   - `Built-in VPD` - Calculated from controller sensors

2. **Tent Probe Sensors** (the 2-plug probe that goes inside your tent)
   - `Tent Temperature` - Your actual tent temperature
   - `Tent Humidity` - Your actual tent humidity
   - `Tent VPD` - Calculated from tent probe sensors
   
   > 💡 **The tent probe (AC-SPC24) is your primary climate monitor** - it measures conditions where your plants are, not where the controller is mounted.

### 🔌 8 Controllable Device Ports

Each port (for fans, lights, humidifiers, etc.) provides:

**Status & Control:**
- Current power level (0-10)
- Online status
- On/Off state
- Remaining time in current cycle
- Next state change timestamp
- Full automation controls (modes, schedules, triggers)

**Comprehensive Automation Data (20+ sensors per port):**
- Target values (temperature, humidity, VPD)
- Trigger thresholds (high/low for temp, humidity, VPD)
- Timer & cycle durations
- Schedule times
- Current automation readings
- Trend indicators (rising/falling)
- Speed settings (on/off)

### 🔬 4 Additional USB Sensor Ports

Connect any combination of:
- **CO2 + Light Sensor (AC-COS3)** - Monitor CO2 and light levels
- **Soil Moisture Sensor (AC-SLS3)** - Track soil water content
- **Water Level Sensor (AC-WDS3)** - Detect water presence
- **Water Temp Sensor** - Monitor reservoir temperature
- **pH Sensor** - Track pH levels
- **EC/TDS Sensor** - Measure nutrient concentration

---

## For Non-AI Controller Owners

You get:
- ✅ Built-in temperature, humidity, and VPD sensors
- ✅ 4 controllable device ports
- ✅ Full automation and scheduling
- ❌ No external USB sensor support (hardware limitation)

---

# Installation

### Via HACS (Custom Repository)

Since this is a fork, you'll need to add it as a custom repository:

1. Open HACS in Home Assistant
2. Click the three dots (⋮) in the top right → **Custom repositories**
3. Add: `https://github.com/JoshuaSeidel/homeassistant-acinfinity`
4. Category: **Integration**
5. Click **Add**
6. Search for **"AC Infinity"** and install
7. Restart Home Assistant

[HACS Documentation](https://hacs.xyz) | [Install HACS](https://hacs.xyz/docs/setup/download)

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/JoshuaSeidel/homeassistant-acinfinity/releases)
2. Extract `custom_components/ac_infinity` to your `config/custom_components/` directory
3. Restart Home Assistant

---

# Setup

## Quick Start

1. **Add Integration**
   - Go to Settings → Devices & Services
   - Click **"+ Add Integration"**
   - Search for **"AC Infinity"**

2. **Login**
   - Enter your AC Infinity account email
   - Enter your password
   - Set polling interval (default: 10 seconds, minimum: 5 seconds)

3. **Enable Entities**
   - Choose what to enable for each controller/port:
     - **All** - Everything (sensors, controls, settings)
     - **Sensors and Settings** - Read sensors, adjust settings
     - **Sensors and Controls** - Read sensors, basic control
     - **Sensors Only** - Just read values (recommended for first setup)
     - **Disable** - Hide this device/port

4. **Done!**
   - Your devices will appear in Home Assistant
   - Sensors update based on your polling interval

## What Appears in Home Assistant

### Your Controller Device
Main device named whatever you called it in the AC Infinity app (e.g., "Grow Tent")

Contains:
- Built-in Temperature
- Built-in Humidity  
- Built-in VPD
- Online status

### Tent Probe Device (AI+ Controllers)
Device named "Your Controller Name **Tent Probe**"

Contains:
- **Tent Temperature** ← Use this for tent climate automations
- **Tent Humidity** ← Use this for tent climate automations
- **Tent VPD** ← Use this for tent climate automations

> 🎯 **These are your primary sensors** - they measure actual tent conditions

### Port Devices (1-8 depending on model)
Each device named "Your Controller Name **Port X Device Name**" (e.g., "Grow Tent Exhaust Fan")

Contains:
- Current Power (0-10)
- Status (Online/Offline)
- State (On/Off)
- Remaining Time
- Next State Change
- Mode controls (Off, On, Auto, Timer, Cycle, Schedule, VPD)
- All automation settings

### Additional Sensor Devices (AI+ Controllers)
Any USB sensors you've connected appear as separate devices:
- CO2 + Light Sensor
- Soil Moisture Sensor
- Water Level Sensor
- etc.

---

# Configuration

## Adjusting Settings

Go to **Settings → Devices & Services → AC Infinity → Configure**

### General Configuration

**Polling Interval**
- How often to check for updates (seconds)
- Minimum: 5 seconds
- Default: 10 seconds
- Lower = more responsive, but more API calls

**Update Password**
- Change your AC Infinity account password
- Requires Home Assistant restart

### Enable / Disable Entities

**Per-Controller Settings**
- Configure each controller independently
- Choose what entities to show for:
  - Controller itself
  - Sensor devices (tent probe, USB sensors)
  - Each port (1-8)

**Options:**
- `All` - Sensors + Controls + Settings
- `Sensors and Settings` - Read sensors, adjust advanced settings
- `Sensors and Controls` - Read sensors, basic on/off control
- `Sensors Only` - Just read data (lowest overhead)
- `Disable` - Hide everything for this device/port

**Tips:**
- Start with "Sensors Only" to see what you have
- Enable controls only for ports you'll automate
- Disable unused ports to reduce entity count
- New controllers auto-add with "Sensors Only"

**⚠️ Using AI Assist in AC Infinity App?**
- If you use AI Assist, keep "Sensors Only" mode
- The AI manages devices automatically from the cloud
- You can monitor but shouldn't manually control devices
- View AI schedules and decisions in the mobile app's "AI" section

**Cleanup:**
Disabled entities remain in Home Assistant until manually deleted at:
`Settings → Devices & Services → Entities`

---

# Examples

## Monitor Tent Climate

```yaml
# Dashboard card showing your actual tent conditions
type: entities
title: Tent Climate
entities:
  - entity: sensor.grow_tent_tent_temperature
    name: Temperature
  - entity: sensor.grow_tent_tent_humidity
    name: Humidity
  - entity: sensor.grow_tent_tent_vpd
    name: VPD
```

## Automation: High Temperature Alert

```yaml
automation:
  - alias: "Tent Too Hot"
    trigger:
      - platform: numeric_state
        entity_id: sensor.grow_tent_tent_temperature
        above: 85
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🌡️ Tent Temperature Alert"
          message: "Tent is {{ states('sensor.grow_tent_tent_temperature') }}°F"
```

## Automation: Boost Fan on High VPD

```yaml
automation:
  - alias: "VPD Control"
    trigger:
      - platform: numeric_state
        entity_id: sensor.grow_tent_tent_vpd
        above: 1.5
    action:
      - service: number.set_value
        target:
          entity_id: number.grow_tent_exhaust_fan_on_power
        data:
          value: 10
```

---

# Troubleshooting

**Tent probe sensors not showing up?**
- Check that probe is plugged into sensor port on controller
- Verify probe appears in AC Infinity mobile app
- Restart Home Assistant
- Check integration configuration

**Only seeing 4 ports instead of 8?**
- Verify you have an AI+ model (CTR89Q or AC-ADA8)
- Check controller firmware is up to date in AC Infinity app

**Sensors not updating?**
- Check polling interval (minimum 5 seconds)
- Verify controller is online in AC Infinity app
- Check Home Assistant logs for API errors

**Too many entities?**
- Use "Sensors Only" for monitoring
- Disable unused ports
- Disable settings entities if you only need controls

---

# Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/JoshuaSeidel/homeassistant-acinfinity/issues)
- **Original Project**: [dalinicus/homeassistant-acinfinity](https://github.com/dalinicus/homeassistant-acinfinity)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

## Credits

This is a fork of the excellent [AC Infinity integration by @dalinicus](https://github.com/dalinicus/homeassistant-acinfinity). This fork focuses on enhanced clarity and documentation specifically for AI+ controller users, while maintaining full compatibility with all supported controllers.

**Original Author**: [@dalinicus](https://github.com/dalinicus)  
**Fork Maintainer**: [@JoshuaSeidel](https://github.com/JoshuaSeidel)

---

## Quick Reference for AI+ Users

### Your Two Sensor Sets

| Sensor Type | What It Measures | Use For |
|-------------|------------------|---------|
| **Tent Temperature/Humidity/VPD** | Inside your grow tent | ✅ All automations |
| **Built-in Temperature/Humidity/VPD** | Inside controller unit | Reference only |

### Your 8 Ports + 4 Sensor USB Ports

- **Ports 1-8**: Connect fans, lights, humidifiers, etc.
- **Sensor Ports 1-4**: Connect tent probe, CO2, soil, water sensors

### Automation Example

```yaml
# Use TENT sensors (not built-in) for climate control
automation:
  - alias: "High Temp Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.your_controller_tent_temperature  # ← Tent sensor!
      above: 85
    action:
      service: notify.mobile_app
      data:
        message: "Tent is too hot!"
```

---

**Made with ❤️ for the AI+ growing community**
