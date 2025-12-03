import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    Platform,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import StateType

from custom_components.ac_infinity.core import (
    ACInfinityController,
    ACInfinityControllerEntity,
    ACInfinityControllerReadOnlyMixin,
    ACInfinityDataUpdateCoordinator,
    ACInfinityEntities,
    ACInfinityEntity,
    ACInfinityDevice,
    ACInfinityDeviceEntity,
    ACInfinityDeviceReadOnlyMixin,
    ACInfinitySensor,
    ACInfinitySensorEntity,
    ACInfinitySensorReadOnlyMixin, enabled_fn_sensor,
)

from .const import (
    DOMAIN,
    ISSUE_URL,
    ControllerPropertyKey,
    CustomDevicePropertyKey,
    DevicePropertyKey,
    DeviceControlKey,
    SensorPropertyKey,
    SensorReferenceKey,
    SensorType, ControllerType,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ACInfinitySensorEntityDescription(SensorEntityDescription):
    """Describes ACInfinity Number Sensor Entities."""

    key: str
    icon: str | None
    translation_key: str | None
    device_class: SensorDeviceClass | None
    native_unit_of_measurement: str | None
    state_class: SensorStateClass | str | None
    suggested_unit_of_measurement: str | None


@dataclass(frozen=True)
class ACInfinityControllerSensorEntityDescription(
    ACInfinitySensorEntityDescription, ACInfinityControllerReadOnlyMixin
):
    """Describes ACInfinity Controller Sensor Entities."""


@dataclass(frozen=True)
class ACInfinitySensorSensorEntityDescription(
    ACInfinitySensorEntityDescription, ACInfinitySensorReadOnlyMixin
):
    """Describes ACInfinity Sensor Sensor Entities"""


@dataclass(frozen=True)
class ACInfinityDeviceSensorEntityDescription(
    ACInfinitySensorEntityDescription, ACInfinityDeviceReadOnlyMixin
):
    """Describes ACInfinity Device Sensor Entities."""


def __suitable_fn_controller_property_default(
    entity: ACInfinityEntity, controller: ACInfinityController
):
    # The AI controller have two temperature measurements; controller temperature and probe temperature.
    # These values are available in the sensor array.  The external values are duplicated on the base fields used by
    # the non-AI controllers. We use the sensor array values as the source of truth, and choose not to duplicate them here
    # by skipping the controller descriptions for the base values.
    return not controller.is_ai_controller and entity.ac_infinity.get_controller_property_exists(
        controller.controller_id, entity.data_key
    )


def __suitable_fn_sensor_default(entity: ACInfinityEntity, sensor: ACInfinitySensor):
    return entity.ac_infinity.get_sensor_property_exists(
        sensor.controller.controller_id,
        sensor.sensor_port,
        sensor.sensor_type,
        SensorPropertyKey.SENSOR_PRECISION,
    ) and entity.ac_infinity.get_sensor_property_exists(
        sensor.controller.controller_id,
        sensor.sensor_port,
        sensor.sensor_type,
        SensorPropertyKey.SENSOR_DATA,
    )


def __get_value_fn_sensor_value_default(
    entity: ACInfinityEntity, sensor: ACInfinitySensor
):
    precision = entity.ac_infinity.get_sensor_property(
        sensor.controller.controller_id,
        sensor.sensor_port,
        sensor.sensor_type,
        SensorPropertyKey.SENSOR_PRECISION,
        1,
    )

    data = entity.ac_infinity.get_sensor_property(
        sensor.controller.controller_id,
        sensor.sensor_port,
        sensor.sensor_type,
        SensorPropertyKey.SENSOR_DATA,
        0,
    )

    # if statement prevents floating point numbers for integer data in the UI
    return data / (10 ** (precision - 1)) if precision > 1 else data


def __suitable_fn_sensor_temperature(
    entity: ACInfinityEntity, sensor: ACInfinitySensor
):
    return (
        entity.ac_infinity.get_sensor_property_exists(
            sensor.controller.controller_id,
            sensor.sensor_port,
            sensor.sensor_type,
            SensorPropertyKey.SENSOR_PRECISION,
        )
        and entity.ac_infinity.get_sensor_property_exists(
            sensor.controller.controller_id,
            sensor.sensor_port,
            sensor.sensor_type,
            SensorPropertyKey.SENSOR_DATA,
        )
        and entity.ac_infinity.get_sensor_property_exists(
            sensor.controller.controller_id,
            sensor.sensor_port,
            sensor.sensor_type,
            SensorPropertyKey.SENSOR_UNIT,
        )
    )


def __get_value_fn_sensor_value_temperature(
    entity: ACInfinityEntity, sensor: ACInfinitySensor
):
    precision = entity.ac_infinity.get_sensor_property(
        sensor.controller.controller_id,
        sensor.sensor_port,
        sensor.sensor_type,
        SensorPropertyKey.SENSOR_PRECISION,
        1,
    )

    data = entity.ac_infinity.get_sensor_property(
        sensor.controller.controller_id,
        sensor.sensor_port,
        sensor.sensor_type,
        SensorPropertyKey.SENSOR_DATA,
        0,
    )

    unit = entity.ac_infinity.get_sensor_property(
        sensor.controller.controller_id,
        sensor.sensor_port,
        sensor.sensor_type,
        SensorPropertyKey.SENSOR_UNIT,
        0,
    )

    value = data / (10 ** (precision - 1)) if precision > 1 else data
    return value if unit > 0 else round((5 * (value - 32) / 9), precision - 1)


def __suitable_fn_device_property_default(entity: ACInfinityEntity, device: ACInfinityDevice):
    return entity.ac_infinity.get_device_property_exists(
        device.controller.controller_id, device.device_port, entity.data_key
    )


def __get_value_fn_device_property_default(
    entity: ACInfinityEntity, device: ACInfinityDevice
):
    return entity.ac_infinity.get_device_property(
        device.controller.controller_id, device.device_port, entity.data_key, 0
    )


def __get_value_fn_floating_point_as_int(
    entity: ACInfinityEntity, controller: ACInfinityController
):
    # value stored as an integer, but represents a 2 digit precision float
    return (
        entity.ac_infinity.get_controller_property(
            controller.controller_id, entity.data_key, 0
        )
        / 100
    )


def __get_next_mode_change_timestamp(
    entity: ACInfinityEntity, device: ACInfinityDevice
) -> datetime | None:
    remaining_seconds = entity.ac_infinity.get_device_property(
        device.controller.controller_id, device.device_port, DevicePropertyKey.REMAINING_TIME, 0
    )

    timezone = entity.ac_infinity.get_controller_property(
        device.controller.controller_id, ControllerPropertyKey.TIME_ZONE
    )

    if remaining_seconds <= 0:
        return None

    return datetime.now(ZoneInfo(timezone)) + timedelta(seconds=remaining_seconds)


CONTROLLER_DESCRIPTIONS: list[ACInfinityControllerSensorEntityDescription] = [
    ACInfinityControllerSensorEntityDescription(
        key=ControllerPropertyKey.TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="temperature",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_controller_property_default,
        get_value_fn=__get_value_fn_floating_point_as_int,
    ),
    ACInfinityControllerSensorEntityDescription(
        key=ControllerPropertyKey.HUMIDITY,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="humidity",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_controller_property_default,
        get_value_fn=__get_value_fn_floating_point_as_int,
    ),
    ACInfinityControllerSensorEntityDescription(
        key=ControllerPropertyKey.VPD,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.KPA,
        suggested_unit_of_measurement=None,
        icon="mdi:water-thermometer",
        translation_key="vapor_pressure_deficit",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_controller_property_default,
        get_value_fn=__get_value_fn_floating_point_as_int,
    ),
]

SENSOR_DESCRIPTIONS: dict[int, ACInfinitySensorSensorEntityDescription] = {
    SensorType.PROBE_TEMPERATURE_F: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.PROBE_TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="probe_temperature",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_temperature,
        get_value_fn=__get_value_fn_sensor_value_temperature,
    ),
    SensorType.PROBE_TEMPERATURE_C: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.PROBE_TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="probe_temperature",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_temperature,
        get_value_fn=__get_value_fn_sensor_value_temperature,
    ),
    SensorType.PROBE_HUMIDITY: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.PROBE_HUMIDITY,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="probe_humidity",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_default,
        get_value_fn=__get_value_fn_sensor_value_default,
    ),
    SensorType.PROBE_VPD: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.PROBE_VPD,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.KPA,
        suggested_unit_of_measurement=None,
        icon="mdi:water-thermometer",
        translation_key="probe_vapor_pressure_deficit",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_default,
        get_value_fn=__get_value_fn_sensor_value_default,
    ),
    SensorType.CONTROLLER_TEMPERATURE_F: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.CONTROLLER_TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="controller_temperature",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_temperature,
        get_value_fn=__get_value_fn_sensor_value_temperature,
    ),
    SensorType.CONTROLLER_TEMPERATURE_C: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.CONTROLLER_TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="controller_temperature",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_temperature,
        get_value_fn=__get_value_fn_sensor_value_temperature,
    ),
    SensorType.CONTROLLER_HUMIDITY: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.CONTROLLER_HUMIDITY,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="controller_humidity",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_default,
        get_value_fn=__get_value_fn_sensor_value_default,
    ),
    SensorType.CONTROLLER_VPD: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.CONTROLLER_VPD,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.KPA,
        suggested_unit_of_measurement=None,
        icon="mdi:water-thermometer",
        translation_key="controller_vapor_pressure_deficit",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_default,
        get_value_fn=__get_value_fn_sensor_value_default,
    ),
    SensorType.CO2: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.CO2_SENSOR,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="co2_sensor",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_default,
        get_value_fn=__get_value_fn_sensor_value_default,
    ),
    SensorType.LIGHT: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.LIGHT_SENSOR,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_unit_of_measurement=None,
        icon="mdi:lightbulb-on-outline",
        translation_key="light_sensor",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_default,
        get_value_fn=__get_value_fn_sensor_value_default,
    ),
    SensorType.SOIL: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.SOIL,
        device_class=SensorDeviceClass.MOISTURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_unit_of_measurement=None,
        icon="mdi:watering-can-outline",
        translation_key="soil_sensor",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_default,
        get_value_fn=__get_value_fn_sensor_value_default,
    ),
    SensorType.WATER_TEMP_F: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.WATER_TEMP,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="water_temperature",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_temperature,
        get_value_fn=__get_value_fn_sensor_value_temperature,
    ),
    SensorType.WATER_TEMP_C: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.WATER_TEMP,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="water_temperature",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_temperature,
        get_value_fn=__get_value_fn_sensor_value_temperature,
    ),
    SensorType.PH: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.PH_SENSOR,
        device_class=SensorDeviceClass.PH,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=None,
        suggested_unit_of_measurement=None,
        icon="mdi:ph",
        translation_key="ph_sensor",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_default,
        get_value_fn=__get_value_fn_sensor_value_default,
    ),
    SensorType.EC: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.EC_SENSOR,
        device_class=SensorDeviceClass.CONDUCTIVITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="µS/cm",
        suggested_unit_of_measurement=None,
        icon="mdi:flash",
        translation_key="ec_sensor",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_default,
        get_value_fn=__get_value_fn_sensor_value_default,
    ),
    SensorType.TDS: ACInfinitySensorSensorEntityDescription(
        key=SensorReferenceKey.TDS_SENSOR,
        device_class=SensorDeviceClass.CONDUCTIVITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="ppm",
        suggested_unit_of_measurement=None,
        icon="mdi:water-opacity",
        translation_key="tds_sensor",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_sensor_default,
        get_value_fn=__get_value_fn_sensor_value_default,
    ),
}

def __suitable_fn_device_control_default(entity: ACInfinityEntity, device: ACInfinityDevice):
    return entity.ac_infinity.get_device_control_exists(
        device.controller.controller_id, device.device_port, entity.data_key
    )


def __get_value_fn_device_control_default(
    entity: ACInfinityEntity, device: ACInfinityDevice
):
    return entity.ac_infinity.get_device_control(
        device.controller.controller_id, device.device_port, entity.data_key, 0
    )


def __get_value_fn_device_control_floating_point(
    entity: ACInfinityEntity, device: ACInfinityDevice
):
    # value stored as an integer, but represents a 2 digit precision float
    return (
        entity.ac_infinity.get_device_control(
            device.controller.controller_id, device.device_port, entity.data_key, 0
        )
        / 100
    )


# Device type mappings for load type display
DEVICE_LOAD_TYPE_NAMES = {
    0: "No Device Type",
    1: "Grow Light",
    2: "Humidifier",
    3: "Dehumidifier",
    4: "Heater",
    5: "AC",
    6: "Fan",
    8: "Water Pump",
    128: "Outlet",
    129: "Grow Light",
    130: "Humidifier",
    131: "Dehumidifier",
    132: "Heater",
    133: "AC",
    134: "Circulation Fan",
    135: "Ventilation Fan",
    136: "Peristaltic Pump",
    137: "Water Pump",
    138: "CO2 Regulator"
}


def __get_value_fn_device_type_name(
    entity: ACInfinityEntity, device: ACInfinityDevice
):
    load_type = entity.ac_infinity.get_device_control(
        device.controller.controller_id, device.device_port, DeviceControlKey.LOAD_TYPE, 0
    )
    return DEVICE_LOAD_TYPE_NAMES.get(load_type, f"Unknown ({load_type})")


def __get_value_fn_port_is_active(
    entity: ACInfinityEntity, device: ACInfinityDevice
):
    # Port is active if it has a device type set or is online
    load_type = entity.ac_infinity.get_device_control(
        device.controller.controller_id, device.device_port, DeviceControlKey.LOAD_TYPE, 0
    )
    is_online = entity.ac_infinity.get_device_property(
        device.controller.controller_id, device.device_port, DevicePropertyKey.ONLINE, 0
    )
    return "Active" if (load_type > 0 or is_online == 1) else "Inactive"


def __get_value_fn_device_sub_device_id(
    entity: ACInfinityEntity, device: ACInfinityDevice
):
    sub_device_id = entity.ac_infinity.get_device_control(
        device.controller.controller_id, device.device_port, "subDeviceId", None
    )
    return sub_device_id if sub_device_id else "None"


DEVICE_DESCRIPTIONS: list[ACInfinityDeviceSensorEntityDescription] = [
    # Port Status Sensors
    ACInfinityDeviceSensorEntityDescription(
        key="port_status",
        device_class=SensorDeviceClass.ENUM,
        state_class=None,
        native_unit_of_measurement=None,
        suggested_unit_of_measurement=None,
        icon="mdi:power-plug",
        translation_key="port_status",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=lambda x, y: True,
        get_value_fn=__get_value_fn_port_is_active,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key="connected_device_type",
        device_class=SensorDeviceClass.ENUM,
        state_class=None,
        native_unit_of_measurement=None,
        suggested_unit_of_measurement=None,
        icon="mdi:devices",
        translation_key="connected_device_type",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_type_name,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.LOAD_TYPE,
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        suggested_unit_of_measurement=None,
        icon="mdi:identifier",
        translation_key="device_load_type_id",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key="subDeviceId",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        suggested_unit_of_measurement=None,
        icon="mdi:barcode",
        translation_key="sub_device_id",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_sub_device_id,
    ),
    # Current Status Sensors
    ACInfinityDeviceSensorEntityDescription(
        key=DevicePropertyKey.SPEAK,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=None,  # no units / bare integer value
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="current_power",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_property_default,
        get_value_fn=__get_value_fn_device_property_default,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DevicePropertyKey.REMAINING_TIME,
        device_class=SensorDeviceClass.DURATION,
        state_class=None,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="remaining_time",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_property_default,
        get_value_fn=__get_value_fn_device_property_default,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=CustomDevicePropertyKey.NEXT_STATE_CHANGE,
        device_class=SensorDeviceClass.TIMESTAMP,
        state_class=None,
        native_unit_of_measurement=None,
        suggested_unit_of_measurement=None,
        icon=None,  # default
        translation_key="next_state_change",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=lambda x, y: True,
        get_value_fn=__get_next_mode_change_timestamp,
    ),
    # Temperature Automation Sensors
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.TARGET_TEMP,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=None,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon="mdi:target",
        translation_key="target_temperature",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.AUTO_TEMP_HIGH_TRIGGER,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=None,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon="mdi:thermometer-chevron-up",
        translation_key="temperature_high_trigger",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.AUTO_TEMP_LOW_TRIGGER,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=None,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon="mdi:thermometer-chevron-down",
        translation_key="temperature_low_trigger",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    # Humidity Automation Sensors
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.TARGET_HUMI,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=None,
        native_unit_of_measurement=PERCENTAGE,
        suggested_unit_of_measurement=None,
        icon="mdi:target",
        translation_key="target_humidity",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.AUTO_HUMIDITY_HIGH_TRIGGER,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=None,
        native_unit_of_measurement=PERCENTAGE,
        suggested_unit_of_measurement=None,
        icon="mdi:water-percent",
        translation_key="humidity_high_trigger",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.AUTO_HUMIDITY_LOW_TRIGGER,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=None,
        native_unit_of_measurement=PERCENTAGE,
        suggested_unit_of_measurement=None,
        icon="mdi:water-percent-alert",
        translation_key="humidity_low_trigger",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    # VPD Automation Sensors
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.TARGET_VPD,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=None,
        native_unit_of_measurement=UnitOfPressure.KPA,
        suggested_unit_of_measurement=None,
        icon="mdi:target",
        translation_key="target_vpd",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.VPD_HIGH_TRIGGER,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=None,
        native_unit_of_measurement=UnitOfPressure.KPA,
        suggested_unit_of_measurement=None,
        icon="mdi:water-thermometer-outline",
        translation_key="vpd_high_trigger",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.VPD_LOW_TRIGGER,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=None,
        native_unit_of_measurement=UnitOfPressure.KPA,
        suggested_unit_of_measurement=None,
        icon="mdi:water-thermometer",
        translation_key="vpd_low_trigger",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    # Timer and Cycle Mode Sensors
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.TIMER_DURATION_TO_ON,
        device_class=SensorDeviceClass.DURATION,
        state_class=None,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        suggested_unit_of_measurement=None,
        icon="mdi:timer",
        translation_key="timer_to_on_minutes",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.TIMER_DURATION_TO_OFF,
        device_class=SensorDeviceClass.DURATION,
        state_class=None,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        suggested_unit_of_measurement=None,
        icon="mdi:timer-off",
        translation_key="timer_to_off_minutes",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.CYCLE_DURATION_ON,
        device_class=SensorDeviceClass.DURATION,
        state_class=None,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        suggested_unit_of_measurement=None,
        icon="mdi:cached",
        translation_key="cycle_on_minutes",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.CYCLE_DURATION_OFF,
        device_class=SensorDeviceClass.DURATION,
        state_class=None,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        suggested_unit_of_measurement=None,
        icon="mdi:cached",
        translation_key="cycle_off_minutes",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
    # Scheduled Times (minutes since midnight)
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.SCHEDULED_START_TIME,
        device_class=None,
        state_class=None,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        suggested_unit_of_measurement=None,
        icon="mdi:clock-start",
        translation_key="schedule_start_time",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.SCHEDULED_END_TIME,
        device_class=None,
        state_class=None,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        suggested_unit_of_measurement=None,
        icon="mdi:clock-end",
        translation_key="schedule_end_time",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
    # Current Readings (what automation sees)
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_unit_of_measurement=None,
        icon=None,
        translation_key="automation_temperature",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.HUMIDITY,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_unit_of_measurement=None,
        icon=None,
        translation_key="automation_humidity",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.VPD_NUMS,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.KPA,
        suggested_unit_of_measurement=None,
        icon="mdi:water-thermometer",
        translation_key="automation_vpd",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_floating_point,
    ),
    # Trend Indicators
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.T_TREND,
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        suggested_unit_of_measurement=None,
        icon="mdi:trending-up",
        translation_key="temperature_trend",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.H_TREND,
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        suggested_unit_of_measurement=None,
        icon="mdi:trending-up",
        translation_key="humidity_trend",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
    # On/Off Speed Settings
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.ON_SPEED,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=None,
        native_unit_of_measurement=None,
        suggested_unit_of_measurement=None,
        icon="mdi:fan",
        translation_key="on_speed",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
    ACInfinityDeviceSensorEntityDescription(
        key=DeviceControlKey.OFF_SPEED,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=None,
        native_unit_of_measurement=None,
        suggested_unit_of_measurement=None,
        icon="mdi:fan-off",
        translation_key="off_speed",
        enabled_fn=enabled_fn_sensor,
        suitable_fn=__suitable_fn_device_control_default,
        get_value_fn=__get_value_fn_device_control_default,
    ),
]


class ACInfinityControllerSensorEntity(ACInfinityControllerEntity, SensorEntity):
    entity_description: ACInfinityControllerSensorEntityDescription

    def __init__(
        self,
        coordinator: ACInfinityDataUpdateCoordinator,
        description: ACInfinityControllerSensorEntityDescription,
        controller: ACInfinityController,
    ) -> None:
        super().__init__(
            coordinator,
            controller,
            description.enabled_fn,
            description.suitable_fn,
            description.key,
            Platform.SENSOR,
        )
        self.entity_description = description

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        return self.entity_description.get_value_fn(self, self.controller)


class ACInfinitySensorSensorEntity(ACInfinitySensorEntity, SensorEntity):
    entity_description: ACInfinitySensorSensorEntityDescription

    def __init__(
        self,
        coordinator: ACInfinityDataUpdateCoordinator,
        description: ACInfinitySensorSensorEntityDescription,
        sensor: ACInfinitySensor,
    ) -> None:
        super().__init__(
            coordinator,
            sensor,
            description.enabled_fn,
            description.suitable_fn,
            description.key,
            Platform.SENSOR,
        )
        self.entity_description = description

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        return self.entity_description.get_value_fn(self, self.sensor)


class ACInfinityDeviceSensorEntity(ACInfinityDeviceEntity, SensorEntity):
    entity_description: ACInfinityDeviceSensorEntityDescription

    def __init__(
        self,
        coordinator: ACInfinityDataUpdateCoordinator,
        description: ACInfinityDeviceSensorEntityDescription,
        device: ACInfinityDevice,
    ) -> None:
        super().__init__(
            coordinator, device, description.enabled_fn, description.suitable_fn, None, description.key, Platform.SENSOR
        )
        self.entity_description = description

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        return self.entity_description.get_value_fn(self, self.device_port)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, add_entities_callback
) -> None:
    """Set up the AC Infinity Platform."""

    coordinator: ACInfinityDataUpdateCoordinator = hass.data[DOMAIN][config.entry_id]

    controllers = coordinator.ac_infinity.get_all_controller_properties()

    entities = ACInfinityEntities(config)
    for controller in controllers:
        for controller_description in CONTROLLER_DESCRIPTIONS:
            controller_entity = ACInfinityControllerSensorEntity(
                coordinator, controller_description, controller
            )
            entities.append_if_suitable(controller_entity)

        for sensor in controller.sensors:
            if sensor.sensor_type in SENSOR_DESCRIPTIONS:
                sensor_description = SENSOR_DESCRIPTIONS[sensor.sensor_type]
                sensor_entity = ACInfinitySensorSensorEntity(
                    coordinator, sensor_description, sensor
                )
                entities.append_if_suitable(sensor_entity)
            elif sensor.sensor_type not in SensorType.__dict__.values():
                logging.warning(
                    'Unknown sensor type "%s". Please fill out an issue at %s with this error message.',
                    sensor.sensor_type,
                    ISSUE_URL,
                )

        for device in controller.devices:
            for device_description in DEVICE_DESCRIPTIONS:
                device_entity = ACInfinityDeviceSensorEntity(
                    coordinator, device_description, device
                )
                entities.append_if_suitable(device_entity)

    add_entities_callback(entities)
