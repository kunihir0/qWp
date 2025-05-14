# Vehicle Sensor Data Quick Reference Guide

This document provides a concise reference for all vehicle sensors available through the HUD Backend system, including typical value ranges, diagnostic significance, and practical applications.

## Engine Sensors

### RPM (Revolutions Per Minute)
- **Typical Range**: 0-8,000 rpm (passenger vehicles), 0-15,000+ rpm (performance vehicles)
- **Idle Range**: 600-1,000 rpm
- **Diagnostic Significance**:
  - Unstable idle: May indicate vacuum leaks, fuel delivery issues, or idle air control problems
  - High idle: Possible throttle body issues or vacuum leaks
  - Low idle: Potential air intake restrictions or sensor issues
- **Unit**: rpm

### Engine Load
- **Typical Range**: 15-30% (idle), 80-100% (full throttle)
- **Diagnostic Significance**: 
  - Consistently high: Possible restrictions in air intake or exhaust
  - Abnormally low under load: Potential fuel delivery issues or sensor problems
- **Unit**: %

### Absolute Load Value
- **Typical Range**: 0-95%
- **Comparison to Engine Load**: Provides a more direct measure of volumetric efficiency
- **Unit**: %

### Relative Engine Load (rel_load)
- **Description**: Calculated engine load relative to its peak output at the current engine speed.
- **Typical Range**: 0-100%
- **Diagnostic Significance**: Provides an indication of how hard the engine is working relative to its maximum capacity at current RPM.
- **Unit**: %

### Engine Friction Torque
- **Typical Range**: 5-15%
- **Significance**: Higher values indicate increased internal engine friction
- **Unit**: %

### Actual Engine Torque
- **Typical Range**: 0-100% (relative to reference torque)
- **Significance**: Direct indicator of engine power output
- **Unit**: %

### Engine Reference Torque
- **Typical Range**: 250-400 Nm (typical passenger car)
- **Significance**: Maximum torque capability of the engine
- **Unit**: Nm

### Driver's Demand Engine Torque (driver_demand_torque)
- **Description**: The percentage of maximum engine torque being requested by the driver via the accelerator pedal.
- **Typical Range**: 0-100%
- **Diagnostic Significance**: Reflects driver input to the engine control system.
- **Unit**: %

## Fuel System

### Fuel Level
- **Typical Range**: 0-100%
- **Diagnostic Significance**: Erratic changes may indicate fuel sender unit issues
- **Unit**: %

### Fuel Pressure
- **Typical Range**: 35-65 psi (240-450 kPa) for port injection, 500-2,000+ psi (3,400-13,800+ kPa) for direct injection
- **Diagnostic Significance**: 
  - Low pressure: Potential fuel pump failure or clogged filter
  - High pressure: Possible fuel pressure regulator issues
- **Unit**: kPa

### Fuel Rail Pressure
- **Typical Range**: 
  - Port Injection: 300-500 kPa
  - Direct Injection: 5,000-20,000 kPa
- **Diagnostic Significance**: Important for fuel delivery and combustion efficiency
- **Unit**: kPa

### Fuel Rail Pressure (Direct Injection) (fuel_rail_pressure_direct)
- **Description**: Measures the fuel pressure directly in the common rail of a direct injection system.
- **Typical Range**: 5,000-30,000+ kPa (varies significantly by system design)
- **Diagnostic Significance**: Critical for precise fuel delivery in GDI/CRDI engines. Deviations can indicate pump, injector, or sensor issues.
- **Unit**: kPa

### Fuel Injection Timing
- **Typical Range**: -30 to +30 degrees
- **Diagnostic Significance**: Critical for emissions control and power
- **Unit**: degrees

### Fuel Rate
- **Typical Range**: 0.5-5 L/h (idle), 5-25+ L/h (cruising/acceleration)
- **Diagnostic Significance**: Direct indicator of fuel consumption and efficiency
- **Unit**: L/h

### Short Term Fuel Trim (Bank 1) (short_fuel_trim_1)
- **Description**: Short-term fuel mixture correction for engine bank 1. This is often labeled as `SHORTFT1` or similar.
- **Typical Range**: -10% to +10%
- **Diagnostic Significance**:
  - Consistently positive: Possible vacuum leaks or low fuel pressure on Bank 1.
  - Consistently negative: Potential issues with MAF sensor or fuel injectors on Bank 1.
- **Unit**: %

### Short Term Fuel Trim (Bank 2) (short_fuel_trim_2)
- **Description**: Short-term fuel mixture correction for engine bank 2. This is often labeled as `SHORTFT2` or similar.
- **Typical Range**: -10% to +10%
- **Diagnostic Significance**:
  - Consistently positive: Possible vacuum leaks or low fuel pressure on Bank 2.
  - Consistently negative: Potential issues with MAF sensor or fuel injectors on Bank 2.
- **Unit**: %

### Long Term Fuel Trim (Bank 1) (long_fuel_trim_1)
- **Description**: Long-term fuel mixture correction for engine bank 1. This is often labeled as `LONGFT1` or similar.
- **Typical Range**: -10% to +10%
- **Diagnostic Significance**: Shows long-term adaptations to fuel system issues on Bank 1.
- **Unit**: %

### Long Term Fuel Trim (Bank 2) (long_fuel_trim_2)
- **Description**: Long-term fuel mixture correction for engine bank 2. This is often labeled as `LONGFT2` or similar.
- **Typical Range**: -10% to +10%
- **Diagnostic Significance**: Shows long-term adaptations to fuel system issues on Bank 2.
- **Unit**: %

### Ethanol Fuel Percentage
- **Typical Range**: 0-85% (depending on fuel type)
- **Diagnostic Significance**: Affects fuel delivery and combustion characteristics
- **Unit**: %

### Fuel Type (fuel_type)
- **Description**: Indicates the type of fuel the vehicle is currently configured to use or is using (e.g., "Gasoline", "Diesel", "LPG", "CNG", "Ethanol").
- **Diagnostic Significance**: Important for engine tuning, emissions calculations, and diagnostics, especially in flex-fuel vehicles.
- **Unit**: string

### Fuel System Status (fuel_system_status)
- **Description**: Indicates the current operating state of the fuel control system.
- **Common States**:
  - "Open loop": ECU uses pre-programmed values (e.g., during warm-up, high load, or certain fault conditions).
  - "Closed loop": ECU uses O2 sensor feedback to adjust fuel mixture for optimal stoichiometry.
  - "Open loop due to driving conditions": (e.g., deceleration, wide open throttle).
  - "Open loop due to system fault": A fault prevents closed-loop operation.
  - "Closed loop, but fault with one O2 sensor": Using other O2 sensors or estimated values.
- **Diagnostic Significance**: Essential for understanding fuel control behavior and diagnosing O2 sensor or other fuel system issues.
- **Unit**: string

## Temperature Sensors

### Coolant Temperature
- **Typical Range**: 80-105°C (176-221°F) when warmed up
- **Diagnostic Significance**: 
  - Overheating: Potential cooling system issues, thermostat failure, or low coolant
  - Underheating: Possible thermostat stuck open
- **Unit**: °C

### Intake Air Temperature
- **Typical Range**: Ambient to 50°C (depends on climate and engine load)
- **Diagnostic Significance**: Affects air density and fuel delivery calculations
- **Unit**: °C

### Ambient Air Temperature
- **Typical Range**: -40 to 50°C (depends on climate)
- **Diagnostic Significance**: Baseline for comparing other temperature readings
- **Unit**: °C

### Engine Oil Temperature
- **Typical Range**: 90-120°C (194-248°F)
- **Diagnostic Significance**: 
  - Excessive: Potential cooling system issues or oil breakdown
  - Too low: May indicate thermostat issues
- **Unit**: °C

### Catalyst Temperature (Bank 1, Sensor 1) (catalyst_temp_b1s1)
- **Description**: Temperature of the catalytic converter at Bank 1, Sensor 1 (typically pre-catalyst or mid-bed).
- **Typical Range**: 400-800°C (752-1472°F) during normal operation after warm-up.
- **Diagnostic Significance**:
  - Too low: Catalyst may not be "lit-off" and operating efficiently.
  - Excessive (>900°C): May indicate engine misfire, overly rich fuel condition, or risk of catalyst damage.
- **Unit**: °C

### Catalyst Temperature (Bank 2, Sensor 1) (catalyst_temp_b2s1)
- **Description**: Temperature of the catalytic converter at Bank 2, Sensor 1 (typically pre-catalyst or mid-bed). Only applicable to V-type engines or engines with dual exhaust banks.
- **Typical Range**: 400-800°C (752-1472°F) during normal operation after warm-up.
- **Diagnostic Significance**:
  - Too low: Catalyst may not be "lit-off" and operating efficiently.
  - Excessive (>900°C): May indicate engine misfire, overly rich fuel condition, or risk of catalyst damage on Bank 2.
- **Unit**: °C

### Fuel Temperature
- **Typical Range**: -20 to 70°C (depends on climate and engine load)
- **Diagnostic Significance**: Affects fuel density and injection calibration
- **Unit**: °C

### Charge Air Cooler Temperature
- **Typical Range**: 30-80°C (turbocharged engines)
- **Diagnostic Significance**: Indicates intercooler efficiency
- **Unit**: °C

## Air & Pressure Sensors

### Mass Air Flow (MAF)
- **Typical Range**: 2-5 g/sec (idle), 15-250 g/sec (acceleration, varies by engine size)
- **Diagnostic Significance**: 
  - Low readings: Potential air intake restrictions or sensor issues
  - High readings: Possible vacuum leaks or sensor contamination
- **Unit**: g/sec

### Manifold Absolute Pressure (MAP)
- **Typical Range**: 
  - 20-30 kPa (vacuum at idle)
  - 80-100 kPa (no vacuum, key on/engine off)
  - 250+ kPa (boosted engines under load)
- **Diagnostic Significance**: Directly related to engine load and power output
- **Unit**: kPa

### Barometric Pressure
- **Typical Range**: 95-105 kPa at sea level, lower at higher altitudes
- **Diagnostic Significance**: Baseline for MAP sensor and affects fuel delivery calculations
- **Unit**: kPa

### Boost Pressure (Turbocharged/Supercharged)
- **Typical Range**: 0-20+ psi (0-140+ kPa) above atmospheric (varies by application)
- **Diagnostic Significance**: Indicates turbocharger/supercharger performance
- **Unit**: kPa

### EVAP System Vapor Pressure
- **Typical Range**: -7 to +7 kPa
- **Diagnostic Significance**: Used for fuel system leak detection
- **Unit**: Pa or kPa

### Absolute EVAP System Vapor Pressure (evap_vapor_pressure_abs)
- **Description**: Measures the absolute pressure within the evaporative emission control (EVAP) system, including atmospheric pressure.
- **Typical Range**: Varies around atmospheric pressure (e.g., 95-105 kPa at sea level). System tests may induce specific vacuum/pressure levels relative to atmospheric.
- **Diagnostic Significance**: Used for detecting leaks in the EVAP system. Comparing this to barometric pressure can give the gauge pressure.
- **Unit**: kPa

## Position & Movement Sensors

### Vehicle Speed
- **Typical Range**: 0-120+ mph (0-200+ km/h)
- **Diagnostic Significance**: Irregular readings may indicate transmission or wheel speed sensor issues
- **Unit**: mph or km/h

### Throttle Position
- **Typical Range**: 0-100%
- **Diagnostic Significance**: Should correlate with accelerator pedal position
- **Unit**: %

### Absolute Throttle Position
- **Typical Range**: 0-100%
- **Diagnostic Significance**: Raw position without adaptations
- **Unit**: %

### Relative Throttle Position
- **Typical Range**: 0-100%
- **Diagnostic Significance**: Position relative to closed and wide open positions
- **Unit**: %

### Accelerator Pedal Position
- **Typical Range**: 0-100%
- **Diagnostic Significance**: Should correlate with throttle position in drive-by-wire systems
- **Unit**: %

### Commanded Throttle Actuator (commanded_throttle)
- **Description**: The throttle opening percentage as commanded by the Engine Control Unit (ECU) to the throttle actuator.
- **Typical Range**: 0-100%
- **Diagnostic Significance**: Comparison with actual throttle position (e.g., `THROTTLE_POS`) can diagnose throttle control system faults, sticking throttle body, or issues with the throttle actuator.
- **Unit**: %

### Timing Advance
- **Typical Range**: 0-40 degrees (varies by engine and load)
- **Diagnostic Significance**: Affects engine performance and emissions
- **Unit**: degrees

## Emissions System

### Oxygen (O2) Sensor 1 Voltage (o2_sensor_1_voltage)
- **Description**: Voltage output from Oxygen Sensor 1. Typically refers to Bank 1, Sensor 1 (B1S1), which is an upstream (pre-catalyst) sensor used for fuel control.
- **Typical Range (Narrowband/Switching Type)**: 0.1V (lean) to 0.9V (rich), fluctuating rapidly in closed-loop operation.
- **Diagnostic Significance (Narrowband/Switching Type)**:
  - Fluctuating (e.g., 5-8 times per 10 seconds): Indicates normal closed-loop fuel control.
  - Steady high (>0.8V): Rich mixture.
  - Steady low (<0.2V): Lean mixture or air leak.
  - Slow response: Aging or contaminated sensor.
- **Note**: Wideband O2 sensors report lambda or current and have different characteristics.
- **Unit**: V

### Oxygen (O2) Sensor 2 Voltage (o2_sensor_2_voltage)
- **Description**: Voltage output from Oxygen Sensor 2. This commonly refers to Bank 1, Sensor 2 (B1S2), a downstream (post-catalyst) sensor used for catalyst monitoring. It could also refer to Bank 2, Sensor 1 (B2S1) on V-engines if `o2_sensor_1_voltage` is B1S1. Context is important.
- **Typical Range (Narrowband/Switching Type, Post-Catalyst)**: Should be relatively stable, often around 0.6-0.8V if the catalyst is efficient and storing oxygen. Fluctuations similar to the upstream sensor indicate poor catalyst efficiency.
- **Diagnostic Significance (Narrowband/Switching Type, Post-Catalyst)**:
  - Steady (e.g., 0.5-0.8V): Indicates good catalyst oxygen storage capacity.
  - Fluctuating like upstream sensor: Poor catalyst efficiency.
  - Stuck high/low: Sensor or wiring fault, or extreme mixture problem.
- **Unit**: V

### Catalyst Temperature
- **Typical Range**: 400-800°C (752-1472°F)
- **Diagnostic Significance**: Critical for emissions control
- **Unit**: °C

### EGR Error
- **Typical Range**: -10 to +10%
- **Diagnostic Significance**: Indicates EGR system performance
- **Unit**: %

### EGR Commanded
- **Typical Range**: 0-100%
- **Diagnostic Significance**: Shows ECU's intended EGR operation
- **Unit**: %

## Electrical System

### Control Module Voltage
- **Typical Range**: 12.6-14.7V (engine running)
- **Diagnostic Significance**: 
  - Below 13.5V: Potential charging system issues
  - Above 15V: Possible voltage regulator failure
- **Unit**: V

### Hybrid Battery Pack Remaining Charge
- **Typical Range**: 20-80% (operating range for hybrid vehicles)
- **Diagnostic Significance**: Battery health and performance indicator
- **Unit**: %

## Vehicle Information

### Vehicle Identification Number (VIN)
- **Format**: 17-character alphanumeric code
- **Significance**: Contains encoded vehicle manufacturer, model, year, and production information

### Diagnostic Trouble Codes (DTCs)
- **Format**: Letter + 4 digits (e.g., P0301)
- **Categories**:
  - P: Powertrain
  - C: Chassis
  - B: Body
  - U: Network/Communication
- **First Digit** (after letter):
  - 0: Generic (SAE standard)
  - 1: Manufacturer-specific

### Malfunction Indicator Lamp (MIL) On (mil_on)
- **Description**: Indicates whether the Malfunction Indicator Lamp (Check Engine Light or Service Engine Soon light) is currently commanded ON by any ECU.
- **Diagnostic Significance**: `True` indicates one or more active diagnostic trouble codes (DTCs) are stored that warrant illuminating the MIL. `False` means the light should be off.
- **Unit**: boolean

### Vehicle Make (vehicle_make)
- **Description**: The manufacturer of the vehicle (e.g., "Ford", "Toyota", "BMW"). Retrieved from vehicle data if available.
- **Unit**: string

### Vehicle Year (vehicle_year)
- **Description**: The model year of the vehicle (e.g., "2023"). Retrieved from vehicle data if available.
- **Unit**: string or integer

### Vehicle Country (vehicle_country)
- **Description**: The country where the vehicle was manufactured, often derived from the VIN. (e.g., "USA", "Germany", "Japan").
- **Unit**: string

### ECU Name (ecu_name)
- **Description**: Identifier for the specific Electronic Control Unit reporting the data (e.g., "Engine Control Module", "PCM", "ECM", "TCM"). This can vary by manufacturer and system.
- **Unit**: string

### OBD Standards (obd_standards)
- **Description**: Specifies the On-Board Diagnostics standard(s) this particular ECU (or vehicle) conforms to (e.g., "EOBD", "OBD-II", "OBD", "JOBD", "WWH-OBD").
- **Unit**: string

## Driving Performance Metrics

### Distance With MIL On
- **Typical Range**: 0-65,535 km
- **Significance**: Regulatory importance, indicates how long vehicle has been driven with fault
- **Unit**: km

### Distance Since DTCs Cleared
- **Typical Range**: 0-65,535 km
- **Significance**: Used for emissions monitoring and readiness
- **Unit**: km

### Runtime Since Engine Start
- **Typical Range**: 0-65,535 seconds
- **Significance**: Used for monitoring short trip patterns
- **Unit**: seconds

### Time Since DTCs Cleared
- **Typical Range**: 0-65,535 minutes
- **Significance**: Used for emissions readiness monitors
- **Unit**: minutes

## Correlations Between Sensors

### Normal Relationships
1. **RPM vs. Vehicle Speed**: Should have consistent relationship in a given gear
2. **Engine Load vs. MAF**: Direct correlation under normal conditions
3. **Coolant Temperature vs. Intake Air Temperature**: Once warmed up, coolant should be higher
4. **Throttle Position vs. MAP/MAF**: Direct relationship under normal conditions
5. **Short Term Fuel Trim vs. O2 Sensor**: Inversely related as system compensates

### Diagnostic Patterns
1. **High RPM + Low Speed**: Potential transmission slippage
2. **High MAF + Low Engine Load**: Possible MAF sensor issues
3. **High Coolant Temperature + Low Oil Temperature**: Potential thermostat issues
4. **High Fuel Trims + Low Fuel Pressure**: Fuel delivery problems
5. **High Catalyst Temperature + Misfires**: Risk of catalyst damage

## Notes on Data Interpretation

1. **Context Matters**: Interpret values based on operating conditions (cold/hot, idle/load)
2. **Correlations**: Look for relationships between different parameters
3. **Trending**: Changes over time often more significant than absolute values
4. **Vehicle Specificity**: Normal ranges vary by vehicle make/model/year
5. **Environmental Factors**: Altitude, temperature, and humidity affect many readings