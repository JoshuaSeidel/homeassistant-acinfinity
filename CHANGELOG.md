# Changelog

# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2024-12-02

### Added
- **Comprehensive Sensor Exposure**: Added 20+ new sensor entities to expose all available automation data
  - Target values for temperature, humidity, and VPD automation
  - High/low trigger thresholds for all automation modes
  - Timer and cycle mode duration settings
  - Schedule start/end times
  - Current automation readings (what the controller is using for decisions)
  - Temperature and humidity trend indicators
  - On/Off speed settings
- All automation parameters now visible for dashboard creation and monitoring
- Clean sensor naming with appropriate device classes and icons

### Changed
- Expanded device sensor descriptions from 3 to 23+ entities per port
- All sensor data now properly typed with Home Assistant device classes

## [1.0.1] - 2024-12-02

### Documentation Updates

**AI Management Clarification**
- Added documentation explaining AI-managed device behavior
- Clarified that when using AI Assist in the AC Infinity app, the AI controls devices automatically
- Updated AI_DATA_REFERENCE.md with AI management section
- Added note about where to view AI schedules and decisions in the app

**Release Process**
- Simplified HACS configuration (removed zip_release requirement)
- Streamlined release workflow

### Notes

When you enable "AI Assist" in the AC Infinity mobile app, the AI takes over device control based on your grow stage and goals. Individual device settings become read-only in the app, and control happens through the AI system. This integration exposes all sensor data and the current state of devices, but the AI's decision-making happens server-side in the AC Infinity cloud.

---

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
