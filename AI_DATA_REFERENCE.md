# AI Controller - Complete Data Reference

## All Available Data for AI+ Controllers

This document lists every piece of data the integration exposes from your AI+ controller.

### Controller Device Data

**Location:** Main controller device (e.g., "Grow Tent")

| Entity | Type | What It Shows |
|--------|------|---------------|
| Built-in Temperature | Sensor | Temperature inside controller unit |
| Built-in Humidity | Sensor | Humidity inside controller unit |
| Built-in VPD | Sensor | VPD calculated from controller sensors |
| Status | Binary Sensor | Controller online/offline |

**Available but not visible as entities:**
- Controller Type (visible in device info)
- MAC Address (visible in device info)
- Firmware Version (visible in device info)
- Hardware Version (visible in device info)
- Port Count (8 for AI+)
- Time Zone

### Tent Probe Data (AC-SPC24)

**Location:** "Your Controller Name Tent Probe" device

| Entity | Type | What It Shows |
|--------|------|---------------|
| Tent Temperature | Sensor | Temperature inside tent |
| Tent Humidity | Sensor | Humidity inside tent |
| Tent VPD | Sensor | VPD calculated from tent probe |

### Each Port (1-8) Data

**Location:** "Your Controller Name Port X Device Name" devices

#### Sensor Entities
| Entity | Type | What It Shows |
|--------|------|---------------|
| Current Power | Sensor | Current fan/device speed (0-10) |
| Status | Binary Sensor | Port online/offline |
| State | Binary Sensor | Device on/off |
| Remaining Time | Sensor | Seconds until next state change |
| Next State Change | Sensor | Timestamp of next change |

#### Control Entities
| Entity | Type | What You Control |
|--------|------|------------------|
| Active Mode | Select | Off, On, Auto, Timer, Cycle, Schedule, VPD |
| On Power | Number | Speed when device is on (0-10) |
| Off Power | Number | Speed when device is off (0-10) |

#### Auto Mode Settings
| Entity | Type | What You Control |
|--------|------|------------------|
| Temperature High Trigger | Number | Turn on above this temp |
| Temperature High Trigger Enabled | Switch | Enable temp high trigger |
| Temperature Low Trigger | Number | Turn on below this temp |
| Temperature Low Trigger Enabled | Switch | Enable temp low trigger |
| Humidity High Trigger | Number | Turn on above this humidity |
| Humidity High Trigger Enabled | Switch | Enable humidity high trigger |
| Humidity Low Trigger | Number | Turn on below this humidity |
| Humidity Low Trigger Enabled | Switch | Enable humidity low trigger |
| Target Temperature | Number | Target temp for regulation |
| Target Temperature Enabled | Switch | Enable target temp mode |
| Target Humidity | Number | Target humidity for regulation |
| Target Humidity Enabled | Switch | Enable target humidity mode |
| Auto Settings Mode | Select | Auto or Target mode |

#### VPD Mode Settings
| Entity | Type | What You Control |
|--------|------|------------------|
| VPD High Trigger | Number | Turn on above this VPD |
| VPD High Trigger Enabled | Switch | Enable VPD high trigger |
| VPD Low Trigger | Number | Turn on below this VPD |
| VPD Low Trigger Enabled | Switch | Enable VPD low trigger |
| Target VPD | Number | Target VPD for regulation |
| Target VPD Enabled | Switch | Enable target VPD mode |
| VPD Settings Mode | Select | VPD mode configuration |

#### Timer Mode Settings
| Entity | Type | What You Control |
|--------|------|------------------|
| Timer Minutes to On | Number | Minutes until device turns on |
| Timer Minutes to Off | Number | Minutes until device turns off |

#### Cycle Mode Settings
| Entity | Type | What You Control |
|--------|------|------------------|
| Cycle Minutes On | Number | Minutes device stays on |
| Cycle Minutes Off | Number | Minutes device stays off |

#### Schedule Mode Settings
| Entity | Type | What You Control |
|--------|------|------------------|
| Scheduled On-Time | Time | Time to turn on |
| Scheduled On-Time Enabled | Switch | Enable scheduled on |
| Scheduled Off-Time | Time | Time to turn off |
| Scheduled Off-Time Enabled | Switch | Enable scheduled off |
| Sunrise/Sunset Minutes | Number | Transition time |
| Sunrise/Sunset Enabled | Switch | Enable sunrise/sunset |

#### Advanced Settings (AI+ Specific)
| Entity | Type | What You Control |
|--------|------|------------------|
| Device Type | Select | Light, Fan, Humidifier, etc. |
| Dynamic Response | Select | Transition or Buffer |
| Temperature Calibration | Number | Adjust temp reading |
| Humidity Calibration | Number | Adjust humidity reading |
| VPD Leaf Temperature Offset | Number | Leaf temp offset for VPD |
| Transition Temperature | Number | Dynamic transition temp |
| Transition Humidity | Number | Dynamic transition humidity |
| Transition VPD | Number | Dynamic transition VPD |
| Buffer Temperature | Number | Dynamic buffer temp |
| Buffer Humidity | Number | Dynamic buffer humidity |
| Buffer VPD | Number | Dynamic buffer VPD |
| Outside Temperature | Select | Neutral, Lower, Higher |
| Outside Humidity | Select | Neutral, Lower, Higher |

### Additional USB Sensors (Ports 1-4)

Each connected USB sensor appears as its own device with relevant data:

**CO2 + Light Sensor (AC-COS3)**
- CO2 (ppm)
- Light Level (%)

**Soil Sensor (AC-SLS3)**
- Soil Moisture (%)

**Water Sensor (AC-WDS3)**
- Water Detection (on/off)

**Water Temperature Sensor**
- Water Temperature

**pH Sensor**
- pH Level

**EC/TDS Sensor**
- EC (μS/cm)
- TDS (ppm)

## How to See Everything

### Method 1: Developer Tools
1. Go to Developer Tools → States
2. Filter by your controller name
3. See all entity states and attributes

### Method 2: Device Page
1. Settings → Devices & Services → AC Infinity
2. Click your controller
3. See all entities grouped by device

### Method 3: Automation
Access any value in automations:
```yaml
# Example: Check if port is an AI controller
{{ state_attr('binary_sensor.grow_tent_status', 'is_ai_controller') }}

# Example: Get current port power
{{ states('sensor.grow_tent_exhaust_fan_current_power') }}
```

## Understanding AI-Managed Devices

### What is AI Assist?

In the AC Infinity mobile app, you can enable "AI Assist" which uses artificial intelligence to automatically manage your grow environment. When AI Assist is active:

**What Changes:**
- ❌ You cannot manually control individual device settings in the app
- ✅ The AI takes over and makes decisions based on your grow stage, goals, and conditions
- ✅ AI creates dynamic schedules and adjusts devices automatically
- ✅ You can view AI's decisions and schedules in the "AI" section of the app

**In Home Assistant:**
- ✅ All sensor data is still available (temperatures, humidity, VPD, etc.)
- ✅ You can see current device states (on/off, power levels)
- ✅ You can see when devices will change state (remaining time, next state change)
- ⚠️ Changing settings in Home Assistant may conflict with AI management
- ℹ️ The AI's decision-making logic happens server-side (not exposed via API)

**Where to See AI Decisions:**
- Open AC Infinity mobile app
- Go to "AI" tab
- View AI's current schedule, decisions, and reasoning
- See why devices are on/off at specific times

### Recommendation

If using AI Assist:
1. Keep "Sensors Only" mode in this integration
2. Monitor conditions via Home Assistant
3. Let the AI handle device control
4. View AI schedules in the mobile app
5. Use Home Assistant for alerts and monitoring automations

If NOT using AI Assist:
1. Enable "All" entities in this integration
2. Full manual control via Home Assistant
3. Create your own automations
4. Set your own schedules and triggers

## What's NOT Available

The following are hardware/API limitations, not integration limitations:

1. **AI Assist Logic** - The AI's decision-making happens in AC Infinity's cloud, not exposed via API
2. **AI Schedules** - AI-created schedules must be viewed in the mobile app's AI section
3. **Internal controller calculations** - The API doesn't expose how VPD is calculated
4. **Historical data** - AC Infinity doesn't provide history, use Home Assistant's history
5. **Direct sensor calibration** - Must be done via AC Infinity app
6. **Firmware updates** - Must be done via AC Infinity app
7. **WiFi settings** - Must be configured via AC Infinity app

## Raw Data Access

If you need to see raw API data for debugging:

1. Enable debug logging in `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.ac_infinity: debug
```

2. Restart Home Assistant
3. Check `home-assistant.log` for API responses

## Summary

**Your AI+ controller exposes:**
- ✅ 3 onboard sensors (built-in temp, humidity, VPD)
- ✅ 3 tent probe sensors (tent temp, humidity, VPD)  
- ✅ 8 ports with full control and monitoring
- ✅ 50+ settings per port (mode, triggers, schedules, calibration, etc.)
- ✅ All connected USB sensors (CO2, soil, water, pH, EC/TDS)
- ✅ Device metadata (type, version, MAC, timezone, etc.)

**That's 100+ data points per AI+ controller!**

Everything the AC Infinity API provides is exposed in Home Assistant.
