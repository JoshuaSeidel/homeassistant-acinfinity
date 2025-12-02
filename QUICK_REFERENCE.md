# AI+ Controller Quick Reference

> **Version 1.0.0** - AI+ Optimized Fork

## 📋 Your Sensors at a Glance

### Climate Monitoring

| Sensor Name | What It Measures | Use For |
|-------------|------------------|---------|
| **Tent Temperature** | Inside your grow tent | ✅ Primary temp monitoring |
| **Tent Humidity** | Inside your grow tent | ✅ Primary humidity monitoring |
| **Tent VPD** | Inside your grow tent | ✅ Climate automations |
| Built-in Temperature | Inside controller unit | Reference only |
| Built-in Humidity | Inside controller unit | Reference only |
| Built-in VPD | Inside controller unit | Reference only |

### 🎯 Golden Rule
**Use "Tent" sensors for all climate control automations!**

---

## 🔌 Your 8 Device Ports

Each port controls a device (fan, light, humidifier, etc.)

**What you can monitor:**
- Current power level (0-10)
- Online status
- On/Off state
- Time remaining in cycle
- Next state change

**What you can control:**
- Mode (Off, On, Auto, Timer, Cycle, Schedule, VPD)
- Power levels
- Temperature triggers
- Humidity triggers
- VPD triggers
- Schedules
- Timers
- Advanced settings

---

## 🔬 Your 4 USB Sensor Ports

**Port 1-4:** Plug in any AC Infinity USB sensor

| Sensor | Model | Measures |
|--------|-------|----------|
| Tent Probe | AC-SPC24 | Temp, Humidity, VPD |
| CO2 + Light | AC-COS3 | CO2, Light intensity |
| Soil Moisture | AC-SLS3 | Soil water content |
| Water Level | AC-WDS3 | Water detection |

Each sensor appears as its own device in Home Assistant!

---

## 🚀 Quick Setup Steps

1. **Install Integration**
   - HACS → Search "AC Infinity" → Install

2. **Add Controller**
   - Settings → Devices & Services → Add Integration
   - Enter AC Infinity credentials

3. **Configure Entities**
   - Choose "Sensors Only" for first setup
   - Enable more features as needed

4. **Verify Tent Probe**
   - Check for "Your Controller Name **Tent Probe**" device
   - Should show: Tent Temperature, Tent Humidity, Tent VPD

5. **Create Automations**
   - Use `sensor.grow_tent_tent_temperature` (not built-in!)
   - Use `sensor.grow_tent_tent_humidity` (not built-in!)
   - Use `sensor.grow_tent_tent_vpd` (not built-in!)

---

## 📊 Sample Dashboard

```yaml
type: vertical-stack
cards:
  - type: glance
    title: 🌱 Tent Climate
    entities:
      - sensor.grow_tent_tent_temperature
      - sensor.grow_tent_tent_humidity
      - sensor.grow_tent_tent_vpd
  
  - type: entities
    title: 💨 Exhaust Fan
    entities:
      - number.grow_tent_exhaust_fan_on_power
      - binary_sensor.grow_tent_exhaust_fan_state
      - sensor.grow_tent_exhaust_fan_current_power
```

---

## 🔧 Common Automations

### High Temp → Max Fan
```yaml
automation:
  - trigger:
      platform: numeric_state
      entity_id: sensor.grow_tent_tent_temperature
      above: 85
    action:
      service: number.set_value
      target:
        entity_id: number.grow_tent_exhaust_fan_on_power
      data:
        value: 10
```

### VPD Too Low → Boost Fan
```yaml
automation:
  - trigger:
      platform: numeric_state
      entity_id: sensor.grow_tent_tent_vpd
      below: 0.8
    action:
      service: number.set_value
      target:
        entity_id: number.grow_tent_exhaust_fan_on_power
      data:
        value: 8
```

### Lights On → Change Fan Mode
```yaml
automation:
  - trigger:
      platform: state
      entity_id: light.grow_tent_grow_lights
      to: 'on'
    action:
      service: select.select_option
      target:
        entity_id: select.grow_tent_exhaust_fan_active_mode
      data:
        option: 'Auto'
```

---

## ⚠️ Troubleshooting

**Tent probe not showing?**
1. Check physical connection to sensor port
2. Verify in AC Infinity mobile app
3. Restart Home Assistant
4. Check entity configuration isn't "Disabled"

**Wrong temperature readings?**
- Check °F vs °C setting in AC Infinity app
- Ensure probe isn't touching hot surfaces
- Keep probe away from direct airflow

**Can't control ports?**
- Change entity config from "Sensors Only" to "All"
- Restart Home Assistant
- Check controller is online

---

## 📞 Support

- [GitHub Issues](https://github.com/JoshuaSeidel/homeassistant-acinfinity/issues)
- [Original Project](https://github.com/dalinicus/homeassistant-acinfinity)
- [Home Assistant Community](https://community.home-assistant.io/)
- [AC Infinity Support](https://acinfinity.com/pages/contact-us)

---

**Controller Model:** UIS Controller AI+ (CTR89Q) / Outlet AI+ (AC-ADA8)  
**Integration Version:** 1.0.0 (AI+ Optimized Fork)  
**Supported:** 8 device ports + 4 USB sensor ports  
**Fork Maintainer:** [@JoshuaSeidel](https://github.com/JoshuaSeidel)
