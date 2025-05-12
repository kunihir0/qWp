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

### Fuel Injection Timing
- **Typical Range**: -30 to +30 degrees
- **Diagnostic Significance**: Critical for emissions control and power
- **Unit**: degrees

### Fuel Rate
- **Typical Range**: 0.5-5 L/h (idle), 5-25+ L/h (cruising/acceleration)
- **Diagnostic Significance**: Direct indicator of fuel consumption and efficiency
- **Unit**: L/h

### Short Term Fuel Trim
- **Typical Range**: -10% to +10%
- **Diagnostic Significance**: 
  - Consistently positive: Possible vacuum leaks or low fuel pressure
  - Consistently negative: Potential issues with MAF sensor or fuel injectors
- **Unit**: %

### Long Term Fuel Trim
- **Typical Range**: -10% to +10%
- **Diagnostic Significance**: Shows long-term adaptations to fuel system issues
- **Unit**: %

### Ethanol Fuel Percentage
- **Typical Range**: 0-85% (depending on fuel type)
- **Diagnostic Significance**: Affects fuel delivery and combustion characteristics
- **Unit**: %

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

### Catalyst Temperature
- **Typical Range**: 400-800°C (752-1472°F) during normal operation
- **Diagnostic Significance**: 
  - Too low: Catalyst may not be operating efficiently
  - Excessive: May indicate engine misfire or rich fuel condition
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

### Timing Advance
- **Typical Range**: 0-40 degrees (varies by engine and load)
- **Diagnostic Significance**: Affects engine performance and emissions
- **Unit**: degrees

## Emissions System

### Oxygen (O2) Sensor Voltage
- **Typical Range**: 0.1-0.9V (fluctuating under normal conditions)
- **Diagnostic Significance**: 
  - Steady high: Rich mixture
  - Steady low: Lean mixture or air leak
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