<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';

// Define interface for OBD data
interface OBDData {
  rpm: number | null;
  speed: number | null;
  rpm_unit: string | null;
  speed_unit: string | null;
  error?: string;
  details?: string;
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

// Current user login
const currentUser = ref('kunihir0');

// Current date/time in UTC format (YYYY-MM-DD HH:MM:SS)
const currentDateTime = ref('2025-05-12 05:28:36');

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

// Compute fill percentages based on current values
const rpmPercentage = computed(() => {
  if (currentRpm.value === null) return 0;
  // Ensure we're calculating a percentage of the max value
  return Math.min(100, Math.max(0, (currentRpm.value / maxRpm) * 100));
});

const speedPercentage = computed(() => {
  if (currentSpeed.value === null) return 0;
  // Ensure we're calculating a percentage of the max value
  return Math.min(100, Math.max(0, (currentSpeed.value / maxSpeed) * 100));
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
      
      if (data.error) {
        lastError.value = `${data.error}${data.details ? ': ' + data.details : ''}`;
        messages.value.push(`Error: ${lastError.value}`);
        return;
      }
      
      currentRpm.value = data.rpm;
      currentSpeed.value = data.speed;
      if (data.rpm_unit) rpmUnit.value = data.rpm_unit;
      if (data.speed_unit) speedUnit.value = data.speed_unit;
      
      messages.value.push(`Data received: RPM=${data.rpm}, Speed=${data.speed}`);
      if (messages.value.length > 50) messages.value.shift(); // Limit log size
      
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
    
    // Try to reconnect if not cleanly closed
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
  // Set up the timer to update date/time
  setInterval(updateDateTime, 1000);
  
  // Simulate some data for development/demo
  if (import.meta.env.DEV) {
    const mockDataInterval = setInterval(() => {
      if (!isConnected.value) {
        currentRpm.value = Math.floor(Math.random() * maxRpm);
        currentSpeed.value = Math.floor(Math.random() * maxSpeed);
      }
    }, 1500);
    
    return () => clearInterval(mockDataInterval);
  }
});

onUnmounted(() => {
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (socket) socket.close();
});

// Format display values
const displayRpm = computed(() => {
  return currentRpm.value !== null ? `${currentRpm.value.toLocaleString()}` : '---';
});

const displaySpeed = computed(() => {
  return currentSpeed.value !== null ? `${currentSpeed.value.toLocaleString()}` : '---';
});

// Generate tick marks for the gauge scales
const rpmTicks = computed(() => {
  const ticks = [];
  const tickCount = 10; // Number of tick marks
  for (let i = 0; i <= tickCount; i++) {
    ticks.push({
      position: i * (100 / tickCount),
      value: Math.round((i / tickCount) * maxRpm)
    });
  }
  return ticks;
});

const speedTicks = computed(() => {
  const ticks = [];
  const tickCount = 10; // Number of tick marks
  for (let i = 0; i <= tickCount; i++) {
    ticks.push({
      position: i * (100 / tickCount),
      value: Math.round((i / tickCount) * maxSpeed)
    });
  }
  return ticks;
});
</script>

<template>
  <div class="car-hud-wrapper">
    <div class="car-hud glass-panel">
      <!-- Top Header Bar -->
      <div class="hud-header glass-panel">
        <div class="header-left">
          <h1>qWp</h1>
        </div>
        <div class="header-center">
          <div class="datetime">{{ currentDateTime }}</div>
        </div>
        <div class="header-right">
          <div class="user-info">
            <span class="user-avatar">👤</span>
            <span class="user-name">{{ currentUser }}</span>
          </div>
          <div class="connection-status">
            <span class="status-label">System Status:</span>
            <span class="status-indicator">
              <span 
                class="status-dot" 
                :class="{
                  'connected': connectionStatus === 'connected',
                  'connecting': connectionStatus === 'connecting',
                  'error': connectionStatus === 'error',
                  'disconnected': connectionStatus === 'disconnected',
                  'pulse': pulseActive
                }"
              ></span>
              {{ connectionStatus.charAt(0).toUpperCase() + connectionStatus.slice(1) }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Error Message (if any) -->
      <div v-if="lastError" class="error-message glass-panel">
        <div class="error-icon">⚠️</div>
        <div class="error-text">{{ lastError }}</div>
      </div>
      
      <!-- Main Content Area - Using a wider horizontal layout -->
      <div class="main-content">
        <!-- Left Column: RPM Gauge -->
        <div class="gauge rpm-gauge glass-panel">
          <div class="gauge-header">
            <div class="gauge-label">Engine RPM</div>
            <div class="gauge-range">0 - {{ maxRpm.toLocaleString() }}</div>
          </div>
          <div class="gauge-display">
            <div class="gauge-value">{{ displayRpm }}</div>
            <div class="gauge-unit">{{ rpmUnit }}</div>
          </div>
          <div class="gauge-bar-container">
            <div class="gauge-bar-background"></div>
            <div 
              class="gauge-bar-fill" 
              :style="{ width: `${rpmPercentage}%` }"
              :class="{ 'high': rpmPercentage > 80 }"
            ></div>
            <div class="gauge-ticks">
              <div 
                v-for="(tick, i) in rpmTicks" 
                :key="`rpm-tick-${i}`"
                class="gauge-tick"
                :style="{ left: `${tick.position}%` }"
              ></div>
            </div>
          </div>
          <div class="gauge-scale">
            <span v-for="(tick, i) in [0, 2, 4, 6, 8, 10]" :key="`rpm-label-${i}`"
                :style="{ left: `${tick * 10}%` }">
              {{ ((tick * maxRpm) / 10).toLocaleString() }}
            </span>
          </div>
        </div>
        
        <!-- Center Column: Vehicle Model -->
        <div class="center-column">
          <div class="vehicle-model-placeholder glass-panel">
            <div class="model-container">
              <div class="model-label">Vehicle Model</div>
              <div class="model-placeholder">
                <div class="car-silhouette"></div>
                <span class="placeholder-text">3D Model Coming Soon</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Right Column: Speed Gauge -->
        <div class="gauge speed-gauge glass-panel">
          <div class="gauge-header">
            <div class="gauge-label">Vehicle Speed</div>
            <div class="gauge-range">0 - {{ maxSpeed.toLocaleString() }}</div>
          </div>
          <div class="gauge-display">
            <div class="gauge-value">{{ displaySpeed }}</div>
            <div class="gauge-unit">{{ speedUnit }}</div>
          </div>
          <div class="gauge-bar-container">
            <div class="gauge-bar-background"></div>
            <div 
              class="gauge-bar-fill" 
              :style="{ width: `${speedPercentage}%` }"
              :class="{ 'high': speedPercentage > 80 }"
            ></div>
            <div class="gauge-ticks">
              <div 
                v-for="(tick, i) in speedTicks" 
                :key="`speed-tick-${i}`"
                class="gauge-tick"
                :style="{ left: `${tick.position}%` }"
              ></div>
            </div>
          </div>
          <div class="gauge-scale">
            <span v-for="(tick, i) in [0, 2, 4, 6, 8, 10]" :key="`speed-label-${i}`"
                :style="{ left: `${tick * 10}%` }">
              {{ ((tick * maxSpeed) / 10).toLocaleString() }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Bottom Row: System Messages Log -->
      <div class="system-log glass-panel">
        <div class="log-header">
          <h2>System Messages</h2>
        </div>
        <div class="log-container">
          <ul class="log-messages">
            <li v-for="(msg, index) in messages.slice().reverse().slice(0, 6)" :key="index"
                :class="{ 
                  'error-log': msg.toLowerCase().includes('error'),
                  'connect-log': msg.toLowerCase().includes('connect')
                }">
              {{ msg }}
            </li>
            <li v-if="messages.length === 0" class="placeholder-log">
              No messages yet. Waiting for data...
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* Global styles to ensure full-width layout */
html, body {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  overflow-x: hidden;
  background-color: #0f1218;
  box-sizing: border-box;
}

*, *:before, *:after {
  box-sizing: inherit;
}
</style>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');

/* CSS Variables */
:root {
  /* Colors */
  --bg-dark: #0f1218;
  --glass-bg: rgba(25, 32, 45, 0.7);
  --glass-border: rgba(255, 255, 255, 0.1);
  --text-primary: #e6e9f0;
  --text-secondary: #a0aec0;
  --accent-primary: #4fd1c5;
  --accent-secondary: #63b3ed;
  --accent-warning: #f6ad55;
  --accent-danger: #fc8181;
  
  /* Status Colors */
  --status-connected: #48bb78;
  --status-connecting: #f6ad55;
  --status-error: #e53e3e;
  --status-disconnected: #718096;
  
  /* UI Elements */
  --border-radius-sm: 8px;
  --border-radius-md: 12px;
  --border-radius-lg: 16px;
  --blur-strength: 10px;
}

/* Main Container - FIXED FOR FULL WIDTH CENTERING */
.car-hud-wrapper {
  font-family: 'Titillium Web', 'Segoe UI', Helvetica, Arial, sans-serif;
  width: 100vw; /* Use viewport width */
  min-height: 100vh;
  display: flex;
  justify-content: center; /* Center horizontally */
  align-items: center; /* Center vertically */
  background-color: var(--bg-dark);
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(79, 209, 197, 0.1), transparent 30%),
    radial-gradient(circle at 80% 10%, rgba(99, 179, 237, 0.1), transparent 30%),
    radial-gradient(circle at 50% 80%, rgba(246, 173, 85, 0.05), transparent 40%);
  color: var(--text-primary);
  padding: 1rem;
  box-sizing: border-box;
}

.car-hud {
  width: 75vw; /* Nearly full viewport width */
  max-width: 1800px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 0; /* Remove padding from container, add to children */
  margin: 0 auto; /* Center horizontally */
}

/* Glassmorphism Style */
.glass-panel {
  background: var(--glass-bg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(var(--blur-strength));
  -webkit-backdrop-filter: blur(var(--blur-strength));
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  padding: 20px;
}

.glass-panel:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}

/* Header Styles */
.hud-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: nowrap; /* Prevent wrapping by default */
}

.header-left {
  display: flex;
  align-items: center;
}

.header-center {
  font-size: 1.2rem;
  font-weight: 500;
  letter-spacing: 1px;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.datetime {
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--border-radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  text-shadow: 0 0 20px rgba(79, 209, 197, 0.6);
  letter-spacing: 1px;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--glass-border);
}

.user-avatar {
  font-size: 1.2rem;
}

.user-name {
  font-weight: 600;
  color: var(--accent-secondary);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-radius: var(--border-radius-md);
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--glass-border);
}

.status-label {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 0.95rem;
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--status-disconnected);
}

.status-dot.connected { background: var(--status-connected); }
.status-dot.connecting { background: var(--status-connecting); }
.status-dot.error { background: var(--status-error); }

/* Pulsing animation for connection status */
.status-dot.pulse {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(72, 187, 120, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(72, 187, 120, 0); }
  100% { box-shadow: 0 0 0 0 rgba(72, 187, 120, 0); }
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  background: rgba(229, 62, 62, 0.15);
  border-color: rgba(229, 62, 62, 0.3);
}

.error-icon {
  font-size: 1.2rem;
}

.error-text {
  font-weight: 600;
  color: #fbd38d;
  word-break: break-word;
}

/* Main Content - WIDE HORIZONTAL LAYOUT */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  gap: 20px;
  height: 350px;
}

/* Center column styling */
.center-column {
  display: flex;
  flex-direction: column;
}

/* Gauge Common Styles */
.gauge {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.gauge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.gauge-label {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.gauge-range {
  font-size: 0.9rem;
  color: var(--text-secondary);
  opacity: 0.7;
}

.gauge-display {
  display: flex;
  align-items: baseline;
  margin-bottom: 20px;
}

.gauge-value {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-right: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.gauge-unit {
  font-size: 1.1rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.gauge-bar-container {
  position: relative;
  height: 15px;
  margin-bottom: 30px;
  width: 100%;
  overflow: hidden;
}

.gauge-bar-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
}

.gauge-bar-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: 8px;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
  max-width: 100%;
}

.gauge-bar-fill.high {
  background: linear-gradient(90deg, var(--accent-warning), var(--accent-danger));
}

/* Gauge ticks */
.gauge-ticks {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.gauge-tick {
  position: absolute;
  width: 2px;
  height: 15px;
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(-50%);
}

/* Scale labels under the gauge */
.gauge-scale {
  position: relative;
  width: 100%;
  height: 24px;
  margin-top: 5px;
  overflow: hidden;
}

.gauge-scale span {
  position: absolute;
  transform: translateX(-50%);
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* Specific Gauge Styles */
.rpm-gauge .gauge-value {
  color: var(--accent-primary);
}

.speed-gauge .gauge-value {
  color: var(--accent-secondary);
}

/* Vehicle Model Placeholder */
.vehicle-model-placeholder {
  height: 100%;
  padding: 0;
  overflow: hidden;
}

.model-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  width: 100%;
  padding: 20px;
}

.model-label {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 15px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.model-placeholder {
  flex: 1;
  width: 100%;
  background: rgba(0, 0, 0, 0.2);
  border: 1px dashed rgba(255, 255, 255, 0.15);
  border-radius: var(--border-radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* Add a simple car silhouette */
.car-silhouette {
  width: 60%;
  height: 40%;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512' fill='%23a0aec0' opacity='0.4'%3E%3Cpath d='M120 32C53.8 32 0 85.8 0 152v144c0 26.5 21.5 48 48 48h32c17.7 0 32-14.3 32-32V227.3c0-15.5-15.1-26.7-29.8-21.9L43.8 224c-9 3-14.7-8.5-7.3-14.7L71.3 181 88.8 166.6c37.2-32.9 85.5-50.6 135.6-50.6H287.4c50.1 0 98.4 17.7 135.6 50.6L440.7 181l34.9 28.3c7.4 6.2 1.7 17.7-7.3 14.7l-38.4-18.6c-14.7-4.8-29.8 6.4-29.8 21.9v84.7c0 17.7 14.3 32 32 32h32c26.5 0 48-21.5 48-48V152C512 85.8 458.2 32 392 32H120zm200 280c0 13.3-10.7 24-24 24H216c-13.3 0-24-10.7-24-24s10.7-24 24-24h80c13.3 0 24 10.7 24 24zM80 304c13.3 0 24 10.7 24 24s-10.7 24-24 24-24-10.7-24-24 10.7-24 24-24zm352 0c13.3 0 24 10.7 24 24s-10.7 24-24 24-24-10.7-24-24 10.7-24 24-24z'/%3E%3C/svg%3E");
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  margin-bottom: 20px;
}

.placeholder-text {
  font-size: 1rem;
  color: var(--text-secondary);
  font-style: italic;
  position: relative;
  z-index: 2;
  padding: 0 15px;
  text-align: center;
}

.model-placeholder::before {
  content: "";
  position: absolute;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(79, 209, 197, 0.05), transparent);
  transform: translateX(-100%);
  animation: shine 3s infinite;
}

@keyframes shine {
  100% { transform: translateX(100%); }
}

/* System Log - FIXED EXPANSION ISSUE */
.system-log {
  width: 100%;
}

.log-header {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-header h2 {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0;
}

.log-container {
  height: 120px; /* Fixed height */
  overflow-y: auto;
  width: 100%;
}

.log-messages {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 10px;
}

.log-messages li {
  padding: 10px 15px;
  border-radius: var(--border-radius-sm);
  background: rgba(0, 0, 0, 0.2);
  font-size: 0.9rem;
  color: var(--text-primary);
  word-break: break-word;
}

.log-messages li.error-log {
  background: rgba(229, 62, 62, 0.1);
  border-left: 3px solid var(--accent-danger);
}

.log-messages li.connect-log {
  background: rgba(72, 187, 120, 0.1);
  border-left: 3px solid var(--accent-primary);
}

.log-messages li.placeholder-log {
  color: var(--text-secondary);
  font-style: italic;
  text-align: center;
  grid-column: 1 / -1;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Responsive adjustments for wide layout */
@media (max-width: 1400px) {
  .main-content {
    height: 320px;
  }
  
  .log-messages {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
  
  .header-right {
    gap: 10px;
  }
}

@media (max-width: 1200px) {
  .main-content {
    height: 300px;
  }
  
  .gauge-value {
    font-size: 2.6rem;
  }
  
  h1 {
    font-size: 1.8rem;
  }
  
  .header-center {
    font-size: 1.1rem;
  }
}

@media (max-width: 1000px) {
  .hud-header {
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .header-center {
    order: 3;
    width: 100%;
    text-align: center;
    margin-top: 10px;
    display: flex;
    justify-content: center;
  }
}

@media (max-width: 900px) {
  .car-hud {
    width: 98vw;
  }
  
  .main-content {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
    height: auto;
    gap: 15px;
  }
  
  .center-column {
    grid-column: span 2;
    grid-row: 2;
  }
  
  .vehicle-model-placeholder {
    height: 200px;
  }
  
  .log-messages {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 650px) {
  .header-right {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .connection-status, .user-info {
    width: 100%;
  }
}

@media (max-width: 600px) {
  .main-content {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(3, auto);
  }
  
  .center-column {
    grid-column: 1;
    grid-row: 2;
  }
  
  .hud-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .datetime {
    margin-top: 5px;
    width: 100%;
    text-align: center;
  }
}
</style>