<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';

// Define an interface for the expected OBD data structure
interface OBDData {
  rpm: number | null;
  speed: number | null;
  rpm_unit: string | null;
  speed_unit: string | null;
  error?: string; // Optional error field
  details?: string; // Optional error details
}

const wsUrl = 'ws://localhost:8765'; // Your Python WebSocket server address
let socket: WebSocket | null = null;

const messages = ref<string[]>([]); // For raw log messages
const connectionStatus = ref<string>('Initializing...');
const lastError = ref<string | null>(null);

// Reactive properties to store OBD data
const currentRpm = ref<number | null>(null);
const currentSpeed = ref<number | null>(null);
const rpmUnit = ref<string | null>('RPM');
const speedUnit = ref<string | null>('kph');

onMounted(() => {
  connectionStatus.value = 'Attempting to connect...';
  console.log('Vue Component Mounted. Attempting to connect to WebSocket...');
  socket = new WebSocket(wsUrl);

  socket.onopen = (event) => {
    console.log('Vue WebSocket ONOPEN event:', event);
    connectionStatus.value = 'Connected';
    messages.value.push('Status: Connected to ' + wsUrl);
    lastError.value = null;
  };

  socket.onmessage = (event) => {
    console.log('Vue WebSocket ONMESSAGE event. Raw Data:', event.data);
    messages.value.push('Raw Server Data: ' + event.data);
    try {
      const data: OBDData = JSON.parse(event.data as string);
      
      if (data.error) {
        // CORRECTED LINE: Use console.error for frontend logging
        console.error('Error message from backend:', data.error, data.details || ''); 
        messages.value.push(`Backend Error: ${data.error} ${data.details || ''}`);
        // Optionally reset values or show error state in UI
        currentRpm.value = null;
        currentSpeed.value = null;
        lastError.value = `${data.error}${data.details ? ': ' + data.details : ''}`;
        return;
      }

      // Update reactive data properties
      currentRpm.value = data.rpm;
      currentSpeed.value = data.speed;
      if (data.rpm_unit) rpmUnit.value = data.rpm_unit;
      if (data.speed_unit) speedUnit.value = data.speed_unit;
      lastError.value = null; // Clear last error on successful data

    } catch (e) {
      console.error('Failed to parse JSON from server:', e);
      messages.value.push('Error: Failed to parse server message. See console.');
      lastError.value = 'Failed to parse server message.';
    }
  };

  socket.onclose = (event) => {
    console.log('Vue WebSocket ONCLOSE event:', event);
    let reason = '';
    if (event.wasClean) {
      reason = 'Connection closed cleanly.';
      connectionStatus.value = 'Connection closed cleanly';
    } else {
      reason = 'Connection died (e.g., server process killed or network error).';
      connectionStatus.value = 'Connection died';
    }
    messages.value.push(`Status: ${reason} Code: ${event.code}, Reason: ${event.reason}`);
    socket = null; 
  };

  socket.onerror = (errorEvent) => { 
    console.error('Vue WebSocket ONERROR event:', errorEvent);
    connectionStatus.value = 'Error connecting';
    messages.value.push('Error: WebSocket error. See console for details. Is the Python server running?');
    lastError.value = 'WebSocket connection error.';
  };
});

onUnmounted(() => {
  console.log('Vue Component Unmounted. Closing WebSocket if open.');
  if (socket) {
    socket.close();
  }
});

// Computed properties for display (optional, but good for formatting)
const displayRpm = computed(() => {
  return currentRpm.value !== null ? `${currentRpm.value} ${rpmUnit.value || 'RPM'}` : 'N/A';
});

const displaySpeed = computed(() => {
  return currentSpeed.value !== null ? `${currentSpeed.value} ${speedUnit.value || 'kph'}` : 'N/A';
});

</script>

<template>
  <div id="hud-container">
    <h1>Real-time HUD Display</h1>
    <p>WebSocket Status: <span :class="connectionStatus.toLowerCase().replace(/\s+/g, '-')">{{ connectionStatus }}</span></p>
    
    <div v-if="lastError" class="error-message">
      Error: {{ lastError }}
    </div>

    <div class="data-display">
      <div class="data-item">
        <h2>Engine RPM</h2>
        <p class="value">{{ displayRpm }}</p>
      </div>
      <div class="data-item">
        <h2>Vehicle Speed</h2>
        <p class="value">{{ displaySpeed }}</p>
      </div>
    </div>

    <div id="raw-log">
      <h2>Raw Message Log:</h2>
      <ul>
        <li v-for="(msg, index) in messages" :key="index">{{ msg }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
#hud-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
  padding: 20px;
  background-color: #f4f7f6; /* Light background for the page */
  border-radius: 8px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

h1 {
  color: #34495e;
}

.status-connected {
  color: green;
  font-weight: bold;
}
.status-connecting, .status-connection-closed-cleanly, .status-connection-died, .status-error-connecting { /* Combined for orange */
  color: orange;
  font-weight: bold;
}
.status-connection-died, .status-error-connecting { /* Override for red */
  color: red;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin: 15px 0;
  border: 1px solid #ef9a9a;
}

.data-display {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  padding: 20px;
  background-color: #ffffff; /* White background for data cards */
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-radius: 8px;
}

.data-item {
  padding: 20px;
  text-align: center;
  min-width: 150px;
}

.data-item h2 {
  margin-top: 0;
  font-size: 1.2em;
  color: #7f8c8d;
}

.data-item .value {
  font-size: 2.5em;
  font-weight: bold;
  color: #2c3e50;
  margin: 5px 0;
}

#raw-log {
  margin-top: 30px;
  text-align: left;
  background-color: #ecf0f1;
  padding: 15px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 0.9em;
}

#raw-log h2 {
  margin-top: 0;
  font-size: 1.1em;
}

#raw-log ul {
  list-style-type: none;
  padding: 0;
}

#raw-log li {
  background-color: #ffffff;
  margin-bottom: 5px;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #bdc3c7;
  word-break: break-all;
}
</style>
