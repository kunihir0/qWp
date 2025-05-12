# HUD Backend WebSocket API Documentation

This document describes the WebSocket API for the HUD Backend application, which provides access to extensive OBD-II vehicle data.

## Connection

### WebSocket Endpoint

```
ws://localhost:8765
```

The WebSocket server is configured to listen on `localhost` port `8765` by default. This can be changed in the `config.py` file.

### Connection Lifecycle

1. Connect to the WebSocket endpoint
2. Receive data automatically (no explicit request required)
3. Data packets are sent at intervals defined by `OBD_POLLING_INTERVAL` (default: 0.5 seconds)
4. The connection remains open until closed by either party

## Data Format

All data is exchanged as JSON. Each message from the server contains the latest available OBD data.

### Example Response

```json
{
  "rpm": 1250.75,
  "rpm_unit": "rpm",
  "speed": 35.42,
  "speed_unit": "mph",
  "coolant_temp": 89,
  "coolant_temp_unit": "celsius",
  "throttle_pos": 15.25,
  "throttle_pos_unit": "%",
  "fuel_level": 75.5,
  "fuel_level_unit": "%",
  "engine_load": 23.4,
  "engine_load_unit": "%",
  "mil_on": false,
  "dtc_count": 0,
  "dtcs": [],
  "status": "OK",
  "vehicle_make": "Toyota (Japan)",
  "vehicle_year": 2019,
  "vehicle_country": "Japan"
}
```

### Status Values

| Status Value | Description |
|--------------|-------------|
| `OK` | Data was retrieved successfully |
| `OBD_DISCONNECTED` | Not connected to OBD interface |
| `OBD_NO_PROTOCOL` | OBD connection established but no protocol detected |
| `OBD_QUERY_ERROR` | Error occurred while querying OBD data |

## Available Data Fields

### Core Engine Parameters

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `rpm` | number | rpm | Engine revolutions per minute |
| `speed` | number | mph | Vehicle speed (converted from km/h to mph) |
| `coolant_temp` | number | celsius | Engine coolant temperature |
| `throttle_pos` | number | % | Throttle position percentage |
| `engine_load` | number | % | Calculated engine load percentage |

### Fuel System

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `fuel_level` | number | % | Fuel tank level percentage |
| `fuel_pressure` | number | kPa | Fuel pressure in intake manifold |
| `fuel_rail_pressure` | number | kPa | Fuel rail pressure |
| `fuel_rail_pressure_direct` | number | kPa | Direct fuel rail pressure (high pressure systems) |
| `fuel_injection_timing` | number | degrees | Fuel injection timing |
| `fuel_rate` | number | L/h | Engine fuel rate |
| `short_fuel_trim_1` | number | % | Short term fuel trim - Bank 1 |
| `long_fuel_trim_1` | number | % | Long term fuel trim - Bank 1 |
| `short_fuel_trim_2` | number | % | Short term fuel trim - Bank 2 |
| `long_fuel_trim_2` | number | % | Long term fuel trim - Bank 2 |
| `fuel_type` | string | - | Type of fuel being used |
| `ethanol_percent` | number | % | Ethanol fuel percentage |
| `fuel_system_status` | string | - | Current fuel system status |

### Air & Intake System

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `intake_temp` | number | celsius | Intake air temperature |
| `maf` | number | grams/sec | Mass Air Flow rate |
| `manifold_pressure` | number | kPa | Intake manifold pressure |
| `boost_pressure` | number | kPa | Boost pressure control |
| `charge_air_temp` | number | celsius | Charge air cooler temperature |

### Emissions System

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `mil_on` | boolean | - | Malfunction Indicator Lamp status (Check Engine Light) |
| `dtc_count` | number | - | Number of Diagnostic Trouble Codes |
| `dtcs` | array | - | List of Diagnostic Trouble Codes with descriptions |
| `o2_sensor_1_voltage` | number | V | Oxygen sensor 1 voltage |
| `o2_sensor_2_voltage` | number | V | Oxygen sensor 2 voltage |
| `catalyst_temp_b1s1` | number | celsius | Catalyst temperature bank 1, sensor 1 |
| `catalyst_temp_b2s1` | number | celsius | Catalyst temperature bank 2, sensor 1 |
| `egr_error` | number | % | Exhaust Gas Recirculation error |
| `egr_commanded` | number | % | Commanded EGR value |
| `evap_vapor_pressure` | number | Pa | Evaporative system vapor pressure |
| `evap_vapor_pressure_abs` | number | kPa | Absolute evap system vapor pressure |

### Temperature Sensors

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `coolant_temp` | number | celsius | Engine coolant temperature |
| `intake_temp` | number | celsius | Intake air temperature |
| `ambient_air_temp` | number | celsius | Ambient air temperature |
| `engine_oil_temp` | number | celsius | Engine oil temperature |
| `fuel_temp` | number | celsius | Fuel temperature |
| `catalyst_temp_b1s1` | number | celsius | Catalyst temperature bank 1, sensor 1 |
| `catalyst_temp_b2s1` | number | celsius | Catalyst temperature bank 2, sensor 1 |

### Vehicle Dynamics

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `timing_advance` | number | degrees | Timing advance |
| `abs_throttle_pos` | number | % | Absolute throttle position |
| `rel_throttle_pos` | number | % | Relative throttle position |
| `accel_pedal_pos` | number | % | Accelerator pedal position |
| `commanded_throttle` | number | % | Commanded throttle actuator control |
| `baro_pressure` | number | kPa | Barometric pressure |
| `abs_load` | number | % | Absolute engine load |
| `rel_load` | number | % | Relative engine load |

### Engine Performance

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `engine_friction_percent` | number | % | Engine friction percentage |
| `driver_demand_torque` | number | % | Driver's demanded engine torque |
| `actual_engine_torque` | number | % | Actual engine torque |
| `engine_ref_torque` | number | Nm | Engine reference torque |

### Battery & Electrical

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `control_module_voltage` | number | V | Control module voltage |
| `hybrid_battery_remaining` | number | % | Hybrid battery pack remaining charge |

### Vehicle Information

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `vin` | string | - | Vehicle Identification Number |
| `ecu_name` | string | - | ECU name/identification |
| `obd_standards` | string | - | OBD standards compliance |
| `vehicle_make` | string | - | Vehicle manufacturer/make (decoded from VIN) |
| `vehicle_year` | number | - | Model year (decoded from VIN) |
| `vehicle_country` | string | - | Country of manufacture (decoded from VIN) |

### Maintenance & Diagnostic

| Field Name | Data Type | Unit | Description |
|------------|-----------|------|-------------|
| `distance_with_mil` | number | km | Distance traveled with MIL on |
| `distance_since_codes_cleared` | number | km | Distance since DTCs cleared |
| `runtime_since_engine_start` | number | seconds | Run time since engine start |
| `time_since_codes_cleared` | number | minutes | Time since DTCs cleared |

## Error Handling

If an error occurs during OBD querying, the response will include:

```json
{
  "status": "OBD_QUERY_ERROR",
  "error_details": "Error message"
}
```

If the OBD connection is not available, the response will include:

```json
{
  "status": "OBD_DISCONNECTED"
}
```

## Message Sending

The WebSocket server currently does not process incoming messages from clients other than logging them. Future versions may support control commands from the client.

## Security Considerations

This API does not implement authentication or encryption. It is designed for local use within a trusted network environment. If exposing to wider networks, additional security measures should be implemented.

## Rate Limiting

Data is streamed at the rate defined by `OBD_POLLING_INTERVAL` in `config.py` (default: 0.5 seconds). This rate can be adjusted based on specific use cases and hardware capabilities.

## Notes on Data Availability

Not all vehicles support all parameters. The response will include only the data fields that the vehicle supports. Fields that are not supported or not available will have a `null` value.