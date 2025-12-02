# Changelog

## [1.0.0] - 2025-12-02

### AI+ Optimized Fork Release

This is the first release of the AI+ optimized fork of the original AC Infinity integration.

#### ✨ New Features

**Clearer Sensor Naming**
- Renamed "Controller" sensors to "Built-in" sensors (Built-in Temperature, Built-in Humidity, Built-in VPD)
- Renamed "Probe" sensors to "Tent" sensors (Tent Temperature, Tent Humidity, Tent VPD)
- Renamed probe device to "Tent Probe" for instant clarity

**Enhanced AI+ Support**
- Added support for water temperature sensors
- Added support for pH sensors
- Added support for EC/TDS sensors
- Full 8-port controller support
- Complete 4 USB sensor port documentation

**Comprehensive Documentation**
- Rewritten README focused on AI+ controller features
- Clear compatibility table showing all controller models
- Step-by-step setup guide with what you'll see in Home Assistant
- Example automations using correct sensor names
- Troubleshooting guide
- Quick reference section

#### 🔧 Improvements

- Device names now clearly indicate purpose (e.g., "Tent Probe" vs "Probe Sensor")
- Better distinction between built-in and external sensors
- AI+ features prominently highlighted
- Installation instructions for fork

#### 📝 Documentation

- Added QUICK_REFERENCE.md for at-a-glance information
- Updated all translations with new sensor names
- Added compatibility information for all controller models

#### 🙏 Credits

This fork is based on the excellent work by [@dalinicus](https://github.com/dalinicus) on the [original AC Infinity integration](https://github.com/dalinicus/homeassistant-acinfinity). All core functionality and API interaction code remains from the original project.

---

## Previous Versions

For changelog of versions prior to the fork, see the [original repository](https://github.com/dalinicus/homeassistant-acinfinity).
