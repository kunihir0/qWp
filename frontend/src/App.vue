<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import HudHeader from './components/HudHeader.vue';
import ErrorMessage from './components/ErrorMessage.vue';
import MilWarning from './components/MilWarning.vue';
import DataGauge from './components/DataGauge.vue';
import FuelGauge from './components/FuelGauge.vue';
import VehicleModelPlaceholder from './components/VehicleModelPlaceholder.vue';
import DtcTable from './components/DtcTable.vue';
import SystemLog from './components/SystemLog.vue';
import SemiCircleGauge from './components/SemiCircleGauge.vue';
import SmallGauge from './components/SmallGauge.vue';

// Define interface for OBD data
interface OBDData {
  // Core Engine Parameters
  rpm: number | null;
  rpm_unit?: string | null;
  speed: number | null;
  speed_unit?: string | null;
  throttle_pos: number | null;
  throttle_pos_unit?: string | null;
  engine_load: number | null;
  engine_load_unit?: string | null;

  // Fuel System
  fuel_level: number | null;
  fuel_level_unit?: string | null;
  fuel_pressure: number | null;
  fuel_pressure_unit?: string | null;
  fuel_rail_pressure: number | null;
  fuel_rail_pressure_unit?: string | null;
  fuel_rail_pressure_direct: number | null;
  fuel_rail_pressure_direct_unit?: string | null;
  fuel_injection_timing: number | null;
  fuel_injection_timing_unit?: string | null;
  fuel_rate: number | null;
  fuel_rate_unit?: string | null;
  short_fuel_trim_1: number | null;
  short_fuel_trim_1_unit?: string | null;
  long_fuel_trim_1: number | null;
  long_fuel_trim_1_unit?: string | null;
  short_fuel_trim_2: number | null;
  short_fuel_trim_2_unit?: string | null;
  long_fuel_trim_2: number | null;
  long_fuel_trim_2_unit?: string | null;
  fuel_type: string | null;
  ethanol_percent: number | null;
  ethanol_percent_unit?: string | null;
  fuel_system_status: string | null;

  // Air & Intake System
  maf: number | null;
  maf_unit?: string | null;
  manifold_pressure: number | null;
  manifold_pressure_unit?: string | null;
  boost_pressure: number | null;
  boost_pressure_unit?: string | null;

  // Emissions System
  mil_on: boolean | null;
  dtc_count: number | null;
  dtcs: { code: string; desc: string }[] | null;
  o2_sensor_1_voltage: number | null;
  o2_sensor_1_voltage_unit?: string | null;
  o2_sensor_2_voltage: number | null;
  o2_sensor_2_voltage_unit?: string | null;
  egr_error: number | null;
  egr_error_unit?: string | null;
  egr_commanded: number | null;
  egr_commanded_unit?: string | null;
  evap_vapor_pressure: number | null;
  evap_vapor_pressure_unit?: string | null;
  evap_vapor_pressure_abs: number | null;
  evap_vapor_pressure_abs_unit?: string | null;

  // Temperature Sensors
  coolant_temp: number | null;
  coolant_temp_unit?: string | null;
  intake_temp: number | null;
  intake_temp_unit?: string | null;
  charge_air_temp: number | null;
  charge_air_temp_unit?: string | null;
  ambient_air_temp: number | null;
  ambient_air_temp_unit?: string | null;
  engine_oil_temp: number | null;
  engine_oil_temp_unit?: string | null;
  fuel_temp: number | null;
  fuel_temp_unit?: string | null;
  catalyst_temp_b1s1: number | null;
  catalyst_temp_b1s1_unit?: string | null;
  catalyst_temp_b2s1: number | null;
  catalyst_temp_b2s1_unit?: string | null;

  // Vehicle Dynamics
  timing_advance: number | null;
  timing_advance_unit?: string | null;
  abs_throttle_pos: number | null;
  abs_throttle_pos_unit?: string | null;
  rel_throttle_pos: number | null;
  rel_throttle_pos_unit?: string | null;
  accel_pedal_pos: number | null;
  accel_pedal_pos_unit?: string | null;
  commanded_throttle: number | null;
  commanded_throttle_unit?: string | null;
  baro_pressure: number | null;
  baro_pressure_unit?: string | null;
  abs_load: number | null;
  abs_load_unit?: string | null;
  rel_load: number | null;
  rel_load_unit?: string | null;

  // Engine Performance
  engine_friction_percent: number | null;
  engine_friction_percent_unit?: string | null;
  driver_demand_torque: number | null;
  driver_demand_torque_unit?: string | null;
  actual_engine_torque: number | null;
  actual_engine_torque_unit?: string | null;
  engine_ref_torque: number | null;
  engine_ref_torque_unit?: string | null;

  // Battery & Electrical
  control_module_voltage: number | null;
  control_module_voltage_unit?: string | null;
  hybrid_battery_remaining: number | null;
  hybrid_battery_remaining_unit?: string | null;

  // Vehicle Information
  vin: string | null;
  ecu_name: string | null;
  obd_standards: string | null;
  vehicle_make: string | null;
  vehicle_year: number | null;
  vehicle_country: string | null;

  // Maintenance & Diagnostic
  distance_with_mil: number | null;
  distance_with_mil_unit?: string | null;
  distance_since_codes_cleared: number | null;
  distance_since_codes_cleared_unit?: string | null;
  runtime_since_engine_start: number | null;
  runtime_since_engine_start_unit?: string | null;
  time_since_codes_cleared: number | null;
  time_since_codes_cleared_unit?: string | null;

  // Status and errors
  status: string | null;
  error_details?: string | null;
}

// Initial state for the comprehensive OBD data
const initialOBDDataState: OBDData = {
  rpm: null, rpm_unit: 'RPM',
  speed: null, speed_unit: 'km/h',
  coolant_temp: null, coolant_temp_unit: '°C',
  throttle_pos: null, throttle_pos_unit: '%',
  fuel_level: null, fuel_level_unit: '%',
  engine_load: null, engine_load_unit: '%',
  mil_on: null,
  dtc_count: null,
  dtcs: null,
  intake_temp: null, intake_temp_unit: '°C',
  maf: null, maf_unit: 'g/s',
  fuel_pressure: null, fuel_pressure_unit: 'kPa',
  ambient_air_temp: null, ambient_air_temp_unit: '°C',
  engine_oil_temp: null, engine_oil_temp_unit: '°C',
  timing_advance: null, timing_advance_unit: '°',
  control_module_voltage: null, control_module_voltage_unit: 'V',
  boost_pressure: null, boost_pressure_unit: 'kPa',
  status: null,
  error_details: null,
  fuel_rail_pressure: null, fuel_rail_pressure_unit: 'kPa',
  fuel_rail_pressure_direct: null, fuel_rail_pressure_direct_unit: 'kPa',
  fuel_injection_timing: null, fuel_injection_timing_unit: '°',
  fuel_rate: null, fuel_rate_unit: 'L/h',
  short_fuel_trim_1: null, short_fuel_trim_1_unit: '%',
  long_fuel_trim_1: null, long_fuel_trim_1_unit: '%',
  short_fuel_trim_2: null, short_fuel_trim_2_unit: '%',
  long_fuel_trim_2: null, long_fuel_trim_2_unit: '%',
  fuel_type: null,
  ethanol_percent: null, ethanol_percent_unit: '%',
  fuel_system_status: null,
  manifold_pressure: null, manifold_pressure_unit: 'kPa',
  o2_sensor_1_voltage: null, o2_sensor_1_voltage_unit: 'V',
  o2_sensor_2_voltage: null, o2_sensor_2_voltage_unit: 'V',
  egr_error: null, egr_error_unit: '%',
  egr_commanded: null, egr_commanded_unit: '%',
  evap_vapor_pressure: null, evap_vapor_pressure_unit: 'Pa',
  evap_vapor_pressure_abs: null, evap_vapor_pressure_abs_unit: 'kPa',
  charge_air_temp: null, charge_air_temp_unit: '°C',
  fuel_temp: null, fuel_temp_unit: '°C',
  catalyst_temp_b1s1: null, catalyst_temp_b1s1_unit: '°C',
  catalyst_temp_b2s1: null, catalyst_temp_b2s1_unit: '°C',
  abs_throttle_pos: null, abs_throttle_pos_unit: '%',
  rel_throttle_pos: null, rel_throttle_pos_unit: '%',
  accel_pedal_pos: null, accel_pedal_pos_unit: '%',
  commanded_throttle: null, commanded_throttle_unit: '%',
  baro_pressure: null, baro_pressure_unit: 'kPa',
  abs_load: null, abs_load_unit: '%',
  rel_load: null, rel_load_unit: '%',
  engine_friction_percent: null, engine_friction_percent_unit: '%',
  driver_demand_torque: null, driver_demand_torque_unit: '%',
  actual_engine_torque: null, actual_engine_torque_unit: '%',
  engine_ref_torque: null, engine_ref_torque_unit: 'Nm',
  hybrid_battery_remaining: null, hybrid_battery_remaining_unit: '%',
  vin: null,
  ecu_name: null,
  obd_standards: null,
  vehicle_make: null,
  vehicle_year: null,
  vehicle_country: null,
  distance_with_mil: null, distance_with_mil_unit: 'km',
  distance_since_codes_cleared: null, distance_since_codes_cleared_unit: 'km',
  runtime_since_engine_start: null, runtime_since_engine_start_unit: 's',
  time_since_codes_cleared: null, time_since_codes_cleared_unit: 'min',
};

// Comprehensive OBD data reactive state
const obdData = reactive<OBDData>({...initialOBDDataState});

// WebSocket configuration
const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8765';
let socket: WebSocket | null = null;
let reconnectTimer: number | null = null;
const MAX_RECONNECT_ATTEMPTS = 5;
const reconnectAttempts = ref(0);
const INITIAL_RECONNECT_DELAY = 1000; // Start with 1 second

// State variables
const connectionStatus = ref<'connected' | 'connecting' | 'disconnected' | 'error'>('disconnected');
const isConnected = computed(() => connectionStatus.value === 'connected');
const lastError = ref<string | null>(null);
const messages = ref<string[]>([]);

// Current user login
const currentUser = ref('kunihir0');

// Current date/time in UTC format (YYYY-MM-DD HH:MM:SS)
const currentDateTime = ref('2025-05-12 05:28:36'); // Initial value, will be updated

// Update the date/time every second with proper UTC format
const updateDateTime = () => {
  const now = new Date();
  const year = now.getUTCFullYear();
  const month = String(now.getUTCMonth() + 1).padStart(2, '0');
  const day = String(now.getUTCDate()).padStart(2, '0');
  const hours = String(now.getUTCHours()).padStart(2, '0');
  const minutes = String(now.getUTCMinutes()).padStart(2, '0');
  const seconds = String(now.getUTCSeconds()).padStart(2, '0');
  currentDateTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

// Configure gauge ranges - these determine the scale of the gauges
const maxRpm = 8000;
const maxSpeed = 220;
const maxCoolantTemp = 140; // typical max coolant temp in celsius
const maxThrottlePos = 100; // throttle position as percentage
const maxEngineLoad = 100; // engine load as percentage

// Configure ranges for additional gauges
const maxIntakeTemp = 100; // typical max intake temp in celsius
const maxOilTemp = 150; // typical max oil temp in celsius
const maxAmbientTemp = 50; // typical max ambient temp in celsius
const maxTimingAdvance = 60; // typical max timing advance in degrees
const maxVoltage = 16; // typical max voltage
const maxBoostPressure = 250; // typical max boost pressure in kPa
const maxManifoldPressure = 120; // kPa, for naturally aspirated or slightly above atmospheric

// Max values for new SmallGauges
const maxMaf = 200; // g/s
const maxFuelPressure = 500; // kPa (can vary widely, common range for port injection)
const maxBaroPressure = 110; // kPa (standard atmospheric pressure is around 101.325 kPa)


// Computed properties for vehicle information
const vehicleMakeDisplay = computed(() => obdData.vehicle_make ?? 'N/A');
const vehicleYearDisplay = computed(() => obdData.vehicle_year ?? 'N/A');
const decodedVin = computed(() => {
  const rawVin = obdData.vin;
  if (typeof rawVin === 'string' && rawVin.startsWith("bytearray(b'") && rawVin.endsWith("')")) {
    return rawVin.substring(14, rawVin.length - 2);
  }
  return rawVin || 'N/A'; // Return rawVin if not in bytearray format, or N/A if null/undefined
});

// Compute fill percentages based on current values
const rpmPercentage = computed(() => {
  if (obdData.rpm === null) return 0;
  return Math.min(100, Math.max(0, (obdData.rpm / maxRpm) * 100));
});

const speedPercentage = computed(() => {
  if (obdData.speed === null) return 0;
  return Math.min(100, Math.max(0, (obdData.speed / maxSpeed) * 100));
});

const coolantTempPercentage = computed(() => {
  if (obdData.coolant_temp === null) return 0;
  return Math.min(100, Math.max(0, (obdData.coolant_temp / maxCoolantTemp) * 100));
});

const throttlePosPercentage = computed(() => {
  if (obdData.throttle_pos === null) return 0;
  return Math.min(100, Math.max(0, (obdData.throttle_pos / maxThrottlePos) * 100));
});

const fuelLevelPercentage = computed(() => {
  if (obdData.fuel_level === null) return 0;
  return Math.min(100, Math.max(0, obdData.fuel_level)); // Assuming fuel level is already a percentage
});

const engineLoadPercentage = computed(() => {
  if (obdData.engine_load === null) return 0;
  return Math.min(100, Math.max(0, (obdData.engine_load / maxEngineLoad) * 100));
});

// Connection indicator pulse animation control
const pulseActive = computed(() => isConnected.value);

// Connect to WebSocket
const connectWebSocket = () => {
  if (socket !== null) return;
  
  connectionStatus.value = 'connecting';
  socket = new WebSocket(wsUrl);
  
  socket.onopen = () => {
    connectionStatus.value = 'connected';
    reconnectAttempts.value = 0;
    messages.value.push(`Connected to ${wsUrl}`);
    lastError.value = null;
  };
  
  socket.onmessage = (event) => {
    try {
      // First verify we have data
      if (!event.data) {
        throw new Error('Empty WebSocket message received');
      }
      
      // Parse the data with validation
      const rawData = event.data as string;
      const receivedData = JSON.parse(rawData) as Partial<OBDData>;
      
      // Log the received data
      console.log("Raw data received from WebSocket:", receivedData);
      
      // Validate the received data has expected format
      if (!receivedData || typeof receivedData !== 'object') {
        throw new Error('Invalid WebSocket message format: not an object');
      }
      
      // Update the comprehensive reactive object
      for (const key in receivedData) {
        if (Object.prototype.hasOwnProperty.call(receivedData, key) && key in obdData) {
          (obdData as any)[key] = (receivedData as any)[key];
        }
      }
      
      // Handle status and errors based on the comprehensive obdData object
      if (obdData.error_details) {
        lastError.value = `Error: ${obdData.error_details}`;
        messages.value.push(lastError.value);
      } else if (obdData.status && obdData.status !== "OK") {
        lastError.value = `OBD Status: ${obdData.status}`;
        messages.value.push(lastError.value);
      } else {
        lastError.value = null; // Clear error if no error_details and status is OK or not an error status
      }

      // SystemLog message for data update
      messages.value.push(`Data updated. Status: ${obdData.status ?? 'N/A'}`);
      if (messages.value.length > 100) messages.value.splice(0, messages.value.length - 100); // Keep last 100 messages
      
    } catch (e) {
      lastError.value = 'Failed to parse server message';
      messages.value.push(`Parse error: ${e instanceof Error ? e.message : String(e)}`);
      console.error("WebSocket message parse error:", e);
      
      // Update connection status to error state when parse errors occur
      // This ensures UI reflects issue with data processing
      connectionStatus.value = 'error';
    }
  };
  
  socket.onclose = (event) => {
    socket = null;
    connectionStatus.value = 'disconnected';
    
    const reason = event.wasClean ? 
      'Connection closed cleanly' : 
      'Connection lost unexpectedly';
    
    messages.value.push(`${reason} (Code: ${event.code})`);
    
    if (!event.wasClean && reconnectAttempts.value < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts.value++;
      
      // Calculate delay with exponential backoff: 1s, 2s, 4s, 8s, 16s
      const delay = INITIAL_RECONNECT_DELAY * Math.pow(2, reconnectAttempts.value - 1);
      
      messages.value.push(`Reconnect attempt ${reconnectAttempts.value}/${MAX_RECONNECT_ATTEMPTS} in ${delay/1000}s...`);
      reconnectTimer = setTimeout(connectWebSocket, delay) as unknown as number;
    } else if (reconnectAttempts.value >= MAX_RECONNECT_ATTEMPTS) {
      messages.value.push('Maximum reconnection attempts reached. Please check server status or refresh page.');
      lastError.value = 'Failed to connect after multiple attempts';
    }
  };
  
  socket.onerror = () => {
    connectionStatus.value = 'error';
    lastError.value = 'WebSocket connection error';
    messages.value.push('WebSocket error occurred. Is the server running?');
  };
};

// Lifecycle hooks
onMounted(() => {
  connectWebSocket();
  updateDateTime(); // Initial call
  setInterval(updateDateTime, 1000);
  
  if (import.meta.env.DEV) {
    const mockDataInterval = setInterval(() => {
      if (connectionStatus.value !== 'connected') { // Simulate if not connected
        obdData.rpm = Math.floor(Math.random() * maxRpm);
        obdData.speed = Math.floor(Math.random() * maxSpeed);
        obdData.coolant_temp = Math.floor(Math.random() * maxCoolantTemp);
        obdData.throttle_pos = Math.floor(Math.random() * maxThrottlePos);
        obdData.engine_load = Math.floor(Math.random() * maxEngineLoad);
        obdData.fuel_level = Math.floor(Math.random() * 100);
        
        // Mock data for additional sensors
        obdData.intake_temp = Math.floor(Math.random() * maxIntakeTemp);
        obdData.engine_oil_temp = Math.floor(Math.random() * maxOilTemp);
        obdData.ambient_air_temp = Math.floor(Math.random() * maxAmbientTemp);
        obdData.timing_advance = Math.floor(Math.random() * maxTimingAdvance);
        obdData.control_module_voltage = 12 + Math.random() * 2; // 12-14V range
        obdData.boost_pressure = Math.floor(Math.random() * maxBoostPressure);
        obdData.maf = Math.floor(Math.random() * maxMaf);
        obdData.fuel_pressure = Math.floor(Math.random() * maxFuelPressure);
        obdData.baro_pressure = 90 + Math.floor(Math.random() * 20); // Simulate 90-110 kPa
        obdData.manifold_pressure = 90 + Math.floor(Math.random() * 15); // Simulate 90-105 kPa for MAP

        const mockMilActive = Math.random() > 0.8;
        obdData.mil_on = mockMilActive;
        obdData.dtc_count = mockMilActive ? Math.floor(Math.random() * 5) + 1 : 0;
        obdData.dtcs = mockMilActive ? [{code: "P0300", desc: "Random Misfire"}, {code: "P0171", desc: "System Too Lean"}] : [];
      }
    }, 1500);
    return () => clearInterval(mockDataInterval);
  }
});

onUnmounted(() => {
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (socket) socket.close();
});

// Generate tick marks for the gauge scales
const rpmTicks = computed(() => {
  const ticks = [];
  const tickCount = 10;
  for (let i = 0; i <= tickCount; i++) {
    ticks.push({ position: i * (100 / tickCount), value: Math.round((i / tickCount) * maxRpm) });
  }
  return ticks;
});

const speedTicks = computed(() => {
  const ticks = [];
  const tickCount = 10;
  for (let i = 0; i <= tickCount; i++) {
    ticks.push({ position: i * (100 / tickCount), value: Math.round((i / tickCount) * maxSpeed) });
  }
  return ticks;
});

const coolantTempTicks = computed(() => {
  const ticks = [];
  const tickCount = 5;
  for (let i = 0; i <= tickCount; i++) {
    ticks.push({ position: i * (100 / tickCount), value: Math.round((i / tickCount) * maxCoolantTemp) });
  }
  return ticks;
});

const percentageTicks = computed(() => { // For gauges like Throttle, Engine Load
  const ticks = [];
  const tickCount = 5;
  for (let i = 0; i <= tickCount; i++) {
    ticks.push({ position: i * (100 / tickCount), value: i * (100 / tickCount) });
  }
  return ticks;
});

// Dynamic class for coolant temperature bar
const coolantBarClass = computed(() => {
  let classes = 'temperature-fill';
  if (coolantTempPercentage.value > 85) classes += ' high';
  else if (coolantTempPercentage.value > 70) classes += ' warning';
  return classes;
});

</script>

<template>
  <div class="car-hud-wrapper">
    <div class="car-hud">
      <HudHeader
        :current-date-time="currentDateTime"
        :current-user="currentUser"
        :connection-status="connectionStatus"
        :pulse-active="pulseActive"
      />
      
      <ErrorMessage :last-error="lastError" />
      
      <MilWarning :mil-active="obdData.mil_on ?? false" :dtc-count="obdData.dtc_count ?? 0" />
      
      <div class="main-content">
        <div class="rpm-gauge-container">
          <SemiCircleGauge
            label="Engine RPM"
            :value="obdData.rpm"
            :unit="obdData.rpm_unit ?? 'RPM'"
            :max-value="maxRpm"
            start-color="rgba(255, 255, 255, 0.7)"
            end-color="rgba(255, 255, 255, 0.9)"
            :major-ticks="5"
            :minor-ticks="20"
            progress-class="rpm-progress"
          />
        </div>
        
        <div class="vehicle-container">
          <VehicleModelPlaceholder
            :vehicle-make="vehicleMakeDisplay"
            :vehicle-year="vehicleYearDisplay"
            :vin="decodedVin"
          />
        </div>
        
        <div class="speed-gauge-container">
          <SemiCircleGauge
            label="Vehicle Speed"
            :value="obdData.speed"
            :unit="obdData.speed_unit ?? 'km/h'"
            :max-value="maxSpeed"
            start-color="rgba(255, 255, 255, 0.7)"
            end-color="rgba(255, 255, 255, 0.9)"
            :major-ticks="5"
            :minor-ticks="20"
            progress-class="speed-progress"
          />
        </div>
        
        <div class="small-gauges-container">
          <!-- Row 1: Primary metrics -->
          <SmallGauge
            label="Coolant Temperature"
            :value="obdData.coolant_temp"
            :unit="obdData.coolant_temp_unit ?? '°C'"
            :max-value="maxCoolantTemp"
            :bar-class="coolantBarClass"
          />
          <SmallGauge
            label="Oil Temperature"
            :value="obdData.engine_oil_temp"
            :unit="obdData.engine_oil_temp_unit ?? '°C'"
            :max-value="maxOilTemp"
            bar-class="oil-temp-bar"
          />
          <SmallGauge
            label="Engine Load"
            :value="obdData.engine_load"
            :unit="obdData.engine_load_unit ?? '%'"
            :max-value="maxEngineLoad"
            bar-class="engine-load-bar"
          />
          <SmallGauge
            label="Fuel Level"
            :value="obdData.fuel_level"
            :unit="obdData.fuel_level_unit ?? '%'"
            :max-value="100"
            :bar-class="fuelLevelPercentage < 20 ? 'fuel-low-bar' : 'fuel-bar'"
          />
          
          <!-- Row 2: Secondary metrics -->
          <SmallGauge
            label="Intake Temperature"
            :value="obdData.intake_temp"
            :unit="obdData.intake_temp_unit ?? '°C'"
            :max-value="maxIntakeTemp"
            bar-class="intake-temp-bar"
          />
          <SmallGauge
            label="Ambient Temperature"
            :value="obdData.ambient_air_temp"
            :unit="obdData.ambient_air_temp_unit ?? '°C'"
            :max-value="maxAmbientTemp"
            bar-class="ambient-temp-bar"
          />
          <SmallGauge
            label="Throttle Position"
            :value="obdData.throttle_pos"
            :unit="obdData.throttle_pos_unit ?? '%'"
            :max-value="maxThrottlePos"
            bar-class="throttle-bar"
          />
          <SmallGauge
            label="Timing Advance"
            :value="obdData.timing_advance"
            :unit="obdData.timing_advance_unit ?? '°'"
            :max-value="maxTimingAdvance"
            bar-class="timing-advance-bar"
          />
          
          <!-- Row 3: Tertiary metrics -->
          <SmallGauge
            label="Battery Voltage"
            :value="obdData.control_module_voltage"
            :unit="obdData.control_module_voltage_unit ?? 'V'"
            :max-value="maxVoltage"
            bar-class="voltage-bar"
          />
          <SmallGauge
            label="Boost Pressure"
            :value="obdData.boost_pressure"
            :unit="obdData.boost_pressure_unit ?? 'kPa'"
            :max-value="maxBoostPressure"
            bar-class="boost-pressure-bar"
          />
          <!-- New Row for MAF, Fuel Pressure, Baro Pressure -->
          <SmallGauge
            label="MAF"
            :value="obdData.maf"
            :unit="obdData.maf_unit ?? 'g/s'"
            :max-value="maxMaf"
            bar-class="maf-bar"
          />
          <SmallGauge
            label="Fuel Pressure"
            :value="obdData.fuel_pressure"
            :unit="obdData.fuel_pressure_unit ?? 'kPa'"
            :max-value="maxFuelPressure"
            bar-class="fuel-pressure-bar"
          />
          <SmallGauge
            label="Baro. Pressure"
            :value="obdData.baro_pressure"
            :unit="obdData.baro_pressure_unit ?? 'kPa'"
            :max-value="maxBaroPressure"
            bar-class="baro-pressure-bar"
          />
          <SmallGauge
            label="Manifold Pressure"
            :value="obdData.manifold_pressure"
            :unit="obdData.manifold_pressure_unit ?? 'kPa'"
            :max-value="maxManifoldPressure"
            bar-class="manifold-pressure-bar"
          />

        </div>
      </div>
      
      <DtcTable
        :dtc-codes="obdData.dtcs ?? []"
        :mil-active="obdData.mil_on ?? false"
        :dtc-count="obdData.dtc_count ?? 0"
      />
      
      <SystemLog :messages="messages" />
    </div>
  </div>
</template>

<style scoped>
/* Main Container - Tesla-inspired styling */
.car-hud-wrapper {
  font-family: 'Titillium Web', 'Segoe UI', Helvetica, Arial, sans-serif;
  font-weight: 300; /* Lighter font for Tesla-like aesthetic */
  width: 100vw;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  background-color: var(--bg-dark);
  /* Simpler background with less gradient for Tesla minimalist look */
  background-image:
    radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.03), transparent 30%),
    radial-gradient(circle at 80% 10%, rgba(255, 255, 255, 0.03), transparent 30%);
  color: var(--text-primary);
  padding: 1.5rem;
  box-sizing: border-box;
  overflow-y: auto;
}

.car-hud {
  width: 100%;
  max-width: 1800px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  margin: 0;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4);
  background: rgba(20, 20, 20, 0.8);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

/* Tesla-inspired layout for main content */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  grid-template-rows: auto auto;
  grid-template-areas:
    "rpm-gauge vehicle speed-gauge"
    "small-gauges small-gauges small-gauges";
  gap: var(--spacing-md);
  width: 100%;
  min-width: 0; /* Prevent grid blowout */
}

.rpm-gauge-container {
  grid-area: rpm-gauge;
  display: flex;
  justify-content: center;
  align-items: center;
}

.vehicle-container {
  grid-area: vehicle;
  display: flex;
  justify-content: center;
  align-items: center;
}

.speed-gauge-container {
  grid-area: speed-gauge;
  display: flex;
  justify-content: center;
  align-items: center;
}

.small-gauges-container {
  grid-area: small-gauges;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: auto auto auto;
  gap: var(--spacing-md);
}

/* Custom classes for gauge styling */
.rpm-progress, .speed-progress {
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Standard white bars for most gauges */
.throttle-bar, .engine-load-bar, .fuel-bar,
.intake-temp-bar, .ambient-temp-bar, .timing-advance-bar,
.voltage-bar, .boost-pressure-bar,
.maf-bar, .fuel-pressure-bar, .baro-pressure-bar, .manifold-pressure-bar {
  background: rgba(255, 255, 255, 0.7);
}

/* Temperature-related bars with color coding */
.oil-temp-bar {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.9));
}

.fuel-low-bar {
  background: var(--accent-danger);
  animation: pulse-warn 1.5s infinite;
}

@keyframes pulse-warn {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}

/* Responsive adjustments */
@media (max-width: 1600px) {
  .car-hud {
    max-width: 1400px;
  }
}

@media (max-width: 1400px) {
  .main-content {
    grid-template-areas:
      "rpm-gauge rpm-gauge speed-gauge speed-gauge"
      "vehicle vehicle vehicle vehicle"
      "small-gauges small-gauges small-gauges small-gauges";
    grid-template-columns: repeat(4, 1fr);
  }
  
  .rpm-gauge-container, .speed-gauge-container {
    padding: 0 var(--spacing-md);
  }
}

@media (max-width: 1000px) {
  .main-content {
    grid-template-areas:
      "vehicle"
      "rpm-gauge"
      "speed-gauge"
      "small-gauges";
    grid-template-columns: 1fr;
  }
  
  .small-gauges-container {
    grid-template-columns: repeat(2, 1fr); /* Adjust to 2 columns */
    grid-template-rows: repeat(7, auto); /* Adjust rows for new gauges: (10 existing + 3 new + 1 placeholder)/2 = 7 */
  }
}

@media (max-width: 600px) {
  .car-hud-wrapper {
    padding: 0.5rem;
  }
  
  .car-hud {
    border-radius: var(--border-radius-md);
    padding: var(--spacing-sm);
    gap: var(--spacing-sm);
  }
  
  .main-content, .small-gauges-container {
    gap: var(--spacing-sm);
  }
  
  .small-gauges-container {
    grid-template-columns: 1fr; /* Single column for very small screens */
    grid-template-rows: auto; /* Let them stack naturally */
  }
}
</style>