<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
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
  // Base data points
  rpm: number | null;
  speed: number | null;
  rpm_unit: string | null;
  speed_unit: string | null;
  coolant_temp: number | null;
  coolant_temp_unit: string | null;
  throttle_pos: number | null;
  throttle_pos_unit: string | null;
  fuel_level: number | null;
  fuel_level_unit: string | null;
  engine_load: number | null;
  engine_load_unit: string | null;
  mil_on: boolean;
  dtc_count: number;
  dtcs: { code: string, desc: string }[];
  
  // Engine and Fuel System
  intake_temp: number | null;
  intake_temp_unit: string | null;
  maf: number | null;
  maf_unit: string | null;
  fuel_pressure: number | null;
  fuel_pressure_unit: string | null;
  
  // Additional Temperatures
  ambient_air_temp: number | null;
  ambient_air_temp_unit: string | null;
  engine_oil_temp: number | null;
  engine_oil_temp_unit: string | null;
  
  // Vehicle/Driving Dynamics
  timing_advance: number | null;
  timing_advance_unit: string | null;
  
  // Battery/Electrical
  control_module_voltage: number | null;
  control_module_voltage_unit: string | null;
  
  // Advanced Engine Data
  boost_pressure: number | null;
  boost_pressure_unit: string | null;
  
  // Status and errors
  status: string;
  error?: string;
  details?: string;
  error_details?: string;
}

// WebSocket configuration
const wsUrl = 'ws://localhost:8765';
let socket: WebSocket | null = null;
let reconnectTimer: number | null = null;
const MAX_RECONNECT_ATTEMPTS = 5;
const reconnectAttempts = ref(0);

// State variables
const connectionStatus = ref<'connected' | 'connecting' | 'disconnected' | 'error'>('disconnected');
const isConnected = computed(() => connectionStatus.value === 'connected');
const currentRpm = ref<number | null>(null);
const currentSpeed = ref<number | null>(null);
const rpmUnit = ref<string>('RPM');
const speedUnit = ref<string>('km/h');
const lastError = ref<string | null>(null);
const messages = ref<string[]>([]);

// New state variables for additional data points
const currentCoolantTemp = ref<number | null>(null);
const coolantTempUnit = ref<string>('°C');
const currentThrottlePos = ref<number | null>(null);
const throttlePosUnit = ref<string>('%');
const currentFuelLevel = ref<number | null>(null);
const fuelLevelUnit = ref<string>('%');
const currentEngineLoad = ref<number | null>(null);
const engineLoadUnit = ref<string>('%');
const milActive = ref<boolean>(false);
const dtcCount = ref<number>(0);
const dtcCodes = ref<{ code: string, desc: string }[]>([]);

// Additional OBD data points from the expanded sensor set
const currentIntakeTemp = ref<number | null>(null);
const intakeTempUnit = ref<string>('°C');
const currentOilTemp = ref<number | null>(null);
const oilTempUnit = ref<string>('°C');
const currentAmbientTemp = ref<number | null>(null);
const ambientTempUnit = ref<string>('°C');
const currentTimingAdvance = ref<number | null>(null);
const timingAdvanceUnit = ref<string>('°');
const currentVoltage = ref<number | null>(null);
const voltageUnit = ref<string>('V');
const currentBoostPressure = ref<number | null>(null);
const boostPressureUnit = ref<string>('kPa');

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

// Compute fill percentages based on current values
const rpmPercentage = computed(() => {
  if (currentRpm.value === null) return 0;
  return Math.min(100, Math.max(0, (currentRpm.value / maxRpm) * 100));
});

const speedPercentage = computed(() => {
  if (currentSpeed.value === null) return 0;
  return Math.min(100, Math.max(0, (currentSpeed.value / maxSpeed) * 100));
});

const coolantTempPercentage = computed(() => {
  if (currentCoolantTemp.value === null) return 0;
  return Math.min(100, Math.max(0, (currentCoolantTemp.value / maxCoolantTemp) * 100));
});

const throttlePosPercentage = computed(() => {
  if (currentThrottlePos.value === null) return 0;
  return Math.min(100, Math.max(0, (currentThrottlePos.value / maxThrottlePos) * 100));
});

const fuelLevelPercentage = computed(() => {
  if (currentFuelLevel.value === null) return 0;
  return Math.min(100, Math.max(0, currentFuelLevel.value)); // Assuming fuel level is already a percentage
});

const engineLoadPercentage = computed(() => {
  if (currentEngineLoad.value === null) return 0;
  return Math.min(100, Math.max(0, (currentEngineLoad.value / maxEngineLoad) * 100));
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
      const data: OBDData = JSON.parse(event.data as string);
      
      if (data.error || data.error_details) {
        lastError.value = `${data.error || ''}${data.details ? ': ' + data.details : ''}${data.error_details ? ': ' + data.error_details : ''}`;
        messages.value.push(`Error: ${lastError.value}`);
        return;
      }
      
      currentRpm.value = data.rpm;
      currentSpeed.value = data.speed;
      if (data.rpm_unit) rpmUnit.value = data.rpm_unit;
      if (data.speed_unit) speedUnit.value = data.speed_unit;
      
      currentCoolantTemp.value = data.coolant_temp;
      if (data.coolant_temp_unit) coolantTempUnit.value = data.coolant_temp_unit;
      
      currentThrottlePos.value = data.throttle_pos;
      if (data.throttle_pos_unit) throttlePosUnit.value = data.throttle_pos_unit;
      
      currentFuelLevel.value = data.fuel_level;
      if (data.fuel_level_unit) fuelLevelUnit.value = data.fuel_level_unit;
      
      currentEngineLoad.value = data.engine_load;
      if (data.engine_load_unit) engineLoadUnit.value = data.engine_load_unit;
      
      // Set additional data values from expanded sensor set
      currentIntakeTemp.value = data.intake_temp;
      if (data.intake_temp_unit) intakeTempUnit.value = data.intake_temp_unit;
      
      currentOilTemp.value = data.engine_oil_temp;
      if (data.engine_oil_temp_unit) oilTempUnit.value = data.engine_oil_temp_unit;
      
      currentAmbientTemp.value = data.ambient_air_temp;
      if (data.ambient_air_temp_unit) ambientTempUnit.value = data.ambient_air_temp_unit;
      
      currentTimingAdvance.value = data.timing_advance;
      if (data.timing_advance_unit) timingAdvanceUnit.value = data.timing_advance_unit;
      
      currentVoltage.value = data.control_module_voltage;
      if (data.control_module_voltage_unit) voltageUnit.value = data.control_module_voltage_unit;
      
      currentBoostPressure.value = data.boost_pressure;
      if (data.boost_pressure_unit) boostPressureUnit.value = data.boost_pressure_unit;
      
      milActive.value = data.mil_on;
      dtcCount.value = data.dtc_count;
      
      if (data.dtcs && Array.isArray(data.dtcs)) {
        dtcCodes.value = data.dtcs;
      } else {
        dtcCodes.value = []; // Clear if not present or invalid
      }
      
      if (data.status && data.status !== "OK") {
        lastError.value = `OBD Status: ${data.status}`;
        messages.value.push(`OBD Status: ${data.status}`);
      } else if (!data.error && !data.error_details) { // Clear error only if no new error and status is OK
        lastError.value = null;
      }
      
      messages.value.push(`Data received: RPM=${data.rpm}, Speed=${data.speed}, Coolant=${data.coolant_temp}${data.coolant_temp_unit}, Throttle=${data.throttle_pos}${data.throttle_pos_unit}`);
      if (messages.value.length > 50) messages.value.shift();
      
    } catch (e) {
      lastError.value = 'Failed to parse server message';
      messages.value.push(`Parse error: ${e}`);
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
      messages.value.push(`Reconnect attempt ${reconnectAttempts.value}/${MAX_RECONNECT_ATTEMPTS}...`);
      reconnectTimer = setTimeout(connectWebSocket, 2000) as unknown as number;
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
        currentRpm.value = Math.floor(Math.random() * maxRpm);
        currentSpeed.value = Math.floor(Math.random() * maxSpeed);
        currentCoolantTemp.value = Math.floor(Math.random() * maxCoolantTemp);
        currentThrottlePos.value = Math.floor(Math.random() * maxThrottlePos);
        currentEngineLoad.value = Math.floor(Math.random() * maxEngineLoad);
        currentFuelLevel.value = Math.floor(Math.random() * 100);
        
        // Mock data for additional sensors
        currentIntakeTemp.value = Math.floor(Math.random() * maxIntakeTemp);
        currentOilTemp.value = Math.floor(Math.random() * maxOilTemp);
        currentAmbientTemp.value = Math.floor(Math.random() * maxAmbientTemp);
        currentTimingAdvance.value = Math.floor(Math.random() * maxTimingAdvance);
        currentVoltage.value = 12 + Math.random() * 2; // 12-14V range
        currentBoostPressure.value = Math.floor(Math.random() * maxBoostPressure);
        
        // milActive.value = Math.random() > 0.8;
        // dtcCount.value = milActive.value ? Math.floor(Math.random() * 5) + 1 : 0;
        // dtcCodes.value = milActive.value ? [{code: "P0300", desc: "Random Misfire"}, {code: "P0171", desc: "System Too Lean"}] : [];
      }
    }, 1500);
    
    return () => clearInterval(mockDataInterval);
  }
});

onUnmounted(() => {
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (socket) socket.close();
});

// Format display values (passed as string props to DataGauge)
const displayRpm = computed(() => currentRpm.value !== null ? `${currentRpm.value.toLocaleString()}` : '---');
const displaySpeed = computed(() => currentSpeed.value !== null ? `${currentSpeed.value.toLocaleString()}` : '---');
const displayCoolantTemp = computed(() => currentCoolantTemp.value !== null ? `${currentCoolantTemp.value.toLocaleString()}` : '---');
const displayThrottlePos = computed(() => currentThrottlePos.value !== null ? `${currentThrottlePos.value.toLocaleString()}` : '---');
const displayFuelLevel = computed(() => currentFuelLevel.value !== null ? `${currentFuelLevel.value.toLocaleString()}` : '---');
const displayEngineLoad = computed(() => currentEngineLoad.value !== null ? `${currentEngineLoad.value.toLocaleString()}` : '---');

// Format display values for additional sensors
const displayIntakeTemp = computed(() => currentIntakeTemp.value !== null ? `${currentIntakeTemp.value.toLocaleString()}` : '---');
const displayOilTemp = computed(() => currentOilTemp.value !== null ? `${currentOilTemp.value.toLocaleString()}` : '---');
const displayAmbientTemp = computed(() => currentAmbientTemp.value !== null ? `${currentAmbientTemp.value.toLocaleString()}` : '---');
const displayTimingAdvance = computed(() => currentTimingAdvance.value !== null ? `${currentTimingAdvance.value.toLocaleString()}` : '---');
const displayVoltage = computed(() => currentVoltage.value !== null ? `${currentVoltage.value.toLocaleString()}` : '---');
const displayBoostPressure = computed(() => currentBoostPressure.value !== null ? `${currentBoostPressure.value.toLocaleString()}` : '---');

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
      
      <MilWarning :mil-active="milActive" :dtc-count="dtcCount" />
      
      <div class="main-content">
        <div class="rpm-gauge-container">
          <SemiCircleGauge
            label="Engine RPM"
            :value="currentRpm"
            :unit="rpmUnit"
            :max-value="maxRpm"
            start-color="rgba(255, 255, 255, 0.7)"
            end-color="rgba(255, 255, 255, 0.9)"
            :major-ticks="5"
            :minor-ticks="20"
            progress-class="rpm-progress"
          />
        </div>
        
        <div class="vehicle-container">
          <VehicleModelPlaceholder />
        </div>
        
        <div class="speed-gauge-container">
          <SemiCircleGauge
            label="Vehicle Speed"
            :value="currentSpeed"
            :unit="speedUnit"
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
            :value="currentCoolantTemp"
            :unit="coolantTempUnit"
            :max-value="maxCoolantTemp"
            :bar-class="coolantBarClass"
          />
          <SmallGauge
            label="Oil Temperature"
            :value="currentOilTemp"
            :unit="oilTempUnit"
            :max-value="maxOilTemp"
            bar-class="oil-temp-bar"
          />
          <SmallGauge
            label="Engine Load"
            :value="currentEngineLoad"
            :unit="engineLoadUnit"
            :max-value="maxEngineLoad"
            bar-class="engine-load-bar"
          />
          <SmallGauge
            label="Fuel Level"
            :value="currentFuelLevel"
            :unit="fuelLevelUnit"
            :max-value="100"
            :bar-class="fuelLevelPercentage < 20 ? 'fuel-low-bar' : 'fuel-bar'"
          />
          
          <!-- Row 2: Secondary metrics -->
          <SmallGauge
            label="Intake Temperature"
            :value="currentIntakeTemp"
            :unit="intakeTempUnit"
            :max-value="maxIntakeTemp"
            bar-class="intake-temp-bar"
          />
          <SmallGauge
            label="Ambient Temperature"
            :value="currentAmbientTemp"
            :unit="ambientTempUnit"
            :max-value="maxAmbientTemp"
            bar-class="ambient-temp-bar"
          />
          <SmallGauge
            label="Throttle Position"
            :value="currentThrottlePos"
            :unit="throttlePosUnit"
            :max-value="maxThrottlePos"
            bar-class="throttle-bar"
          />
          <SmallGauge
            label="Timing Advance"
            :value="currentTimingAdvance"
            :unit="timingAdvanceUnit"
            :max-value="maxTimingAdvance"
            bar-class="timing-advance-bar"
          />
          
          <!-- Row 3: Tertiary metrics -->
          <SmallGauge
            label="Battery Voltage"
            :value="currentVoltage"
            :unit="voltageUnit"
            :max-value="maxVoltage"
            bar-class="voltage-bar"
          />
          <SmallGauge
            label="Boost Pressure"
            :value="currentBoostPressure"
            :unit="boostPressureUnit"
            :max-value="maxBoostPressure"
            bar-class="boost-pressure-bar"
          />
        </div>
      </div>
      
      <DtcTable
        :dtc-codes="dtcCodes"
        :mil-active="milActive"
        :dtc-count="dtcCount"
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
.voltage-bar, .boost-pressure-bar {
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
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(5, auto);
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
    grid-template-columns: 1fr;
  }
}
</style>