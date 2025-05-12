# HUD Backend Application

A modular Python application for connecting to OBD interfaces and streaming vehicle data via WebSockets.

## Modular Structure

The application has been organized into the following modules:

- **config.py**: Contains all configurable parameters
- **logger_setup.py**: Centralizes logging configuration
- **obd_connection.py**: Manages OBD connection lifecycle
- **obd_data.py**: Handles OBD data querying and processing
- **websocket_server.py**: Manages WebSocket connections and client communication
- **main.py**: Orchestrates application initialization and startup

## Running the Application

### Normal Operation

To run the complete application:

```bash
python main.py
```

This will:
1. Initialize logging
2. Connect to the OBD interface
3. Start the WebSocket server
4. Begin serving data to connected clients

### Running Individual Components

For testing or development, you can run the WebSocket server directly:

```bash
python websocket_server.py
```

## Extending the Application

### Adding New OBD Parameters

To add new OBD parameters, modify the `query_obd_data` function in `obd_data.py`:

1. Add the new parameter to the `data_to_send` dictionary
2. Add the OBD command to `commands_to_query` list
3. Add processing logic for the new parameter

Example:
```python
# Add to data_to_send dictionary
data_to_send["intake_temp"] = None
data_to_send["intake_temp_unit"] = "celsius"

# Add to commands_to_query list
commands_to_query.append(obd.commands.INTAKE_TEMP)

# Add processing logic
if responses["INTAKE_TEMP"] and not responses["INTAKE_TEMP"].is_null():
    data_to_send["intake_temp"] = responses["INTAKE_TEMP"].value.magnitude if hasattr(responses["INTAKE_TEMP"].value, 'magnitude') else responses["INTAKE_TEMP"].value
    data_to_send["intake_temp_unit"] = str(responses["INTAKE_TEMP"].unit)
```

### Adding New Communication Protocols

To add a new communication protocol:

1. Create a new module (e.g., `mqtt_server.py`)
2. Implement the server functionality similar to `websocket_server.py`
3. Add initialization to `main.py`

## Configuration

All configurable parameters are centralized in `config.py`. Modify this file to change:

- WebSocket server host/port
- OBD connection parameters
- Polling intervals
- Other application settings

## Logging

Logging is configured in `logger_setup.py`. The application uses hierarchical loggers:

- `HUD_Backend`: Main application logger
- `obd`: OBD library logger
- `websockets`: WebSockets library logger

Logs are output to the console with timestamps and log levels.

## Available OBD Parameters

The application supports a comprehensive set of OBD-II parameters. Note that not all vehicles support all parameters.

### Currently Implemented in Original Version
- **rpm**: Engine RPM
- **speed**: Vehicle speed (converted to mph)
- **coolant_temp**: Engine coolant temperature
- **throttle_pos**: Throttle position percentage
- **fuel_level**: Fuel tank level percentage
- **engine_load**: Calculated engine load percentage
- **mil_on**: Malfunction Indicator Lamp status (Check Engine Light)
- **dtc_count**: Number of Diagnostic Trouble Codes
- **dtcs**: List of Diagnostic Trouble Codes with descriptions

### Engine and Fuel System
- **intake_temp**: Intake air temperature
- **maf**: Mass Air Flow rate
- **fuel_pressure**: Fuel pressure in intake manifold
- **fuel_rail_pressure**: Fuel rail pressure
- **fuel_rail_pressure_direct**: Direct fuel rail pressure (high pressure systems)
- **fuel_injection_timing**: Fuel injection timing
- **fuel_rate**: Engine fuel rate
- **short_fuel_trim_1**: Short term fuel trim - Bank 1
- **long_fuel_trim_1**: Long term fuel trim - Bank 1
- **short_fuel_trim_2**: Short term fuel trim - Bank 2
- **long_fuel_trim_2**: Long term fuel trim - Bank 2
- **fuel_type**: Type of fuel being used
- **ethanol_percent**: Ethanol fuel percentage
- **evap_vapor_pressure**: Evaporative system vapor pressure

### Emissions System
- **o2_sensor_1_voltage**: Oxygen sensor 1 voltage
- **o2_sensor_2_voltage**: Oxygen sensor 2 voltage
- **catalyst_temp_b1s1**: Catalyst temperature bank 1, sensor 1
- **catalyst_temp_b2s1**: Catalyst temperature bank 2, sensor 1
- **egr_error**: Exhaust Gas Recirculation error
- **egr_commanded**: Commanded EGR value
- **evap_vapor_pressure_abs**: Absolute evap system vapor pressure

### Additional Temperatures
- **ambient_air_temp**: Ambient air temperature
- **engine_oil_temp**: Engine oil temperature
- **fuel_temp**: Fuel temperature

### Vehicle/Driving Dynamics
- **timing_advance**: Timing advance
- **abs_throttle_pos**: Absolute throttle position
- **rel_throttle_pos**: Relative throttle position
- **accel_pedal_pos**: Accelerator pedal position
- **commanded_throttle**: Commanded throttle actuator control
- **manifold_pressure**: Intake manifold pressure
- **baro_pressure**: Barometric pressure
- **abs_load**: Absolute engine load
- **rel_load**: Relative engine load
- **distance_with_mil**: Distance traveled with MIL on
- **distance_since_codes_cleared**: Distance since DTCs cleared
- **runtime_since_engine_start**: Run time since engine start
- **time_since_codes_cleared**: Time since DTCs cleared

### Battery/Electrical
- **control_module_voltage**: Control module voltage
- **hybrid_battery_remaining**: Hybrid battery pack remaining charge

### Advanced Engine Data
- **engine_friction_percent**: Engine friction percentage
- **driver_demand_torque**: Driver's demanded engine torque
- **actual_engine_torque**: Actual engine torque
- **engine_ref_torque**: Engine reference torque
- **boost_pressure**: Boost pressure control
- **charge_air_temp**: Charge air cooler temperature

### Vehicle Information
- **vin**: Vehicle Identification Number
- **ecu_name**: ECU name/identification
- **fuel_system_status**: Fuel system status
- **obd_standards**: OBD standards compliance
- **vehicle_make**: Vehicle manufacturer/make (decoded from VIN)
- **vehicle_year**: Model year (decoded from VIN)
- **vehicle_country**: Country of manufacture (decoded from VIN)