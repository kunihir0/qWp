<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const wsUrl = 'ws://localhost:8765';
let socket: WebSocket | null = null;

const messages = ref<string[]>([]);
const messageToSend = ref<string>('');
const connectionStatus = ref<string>('Initializing...'); // Changed initial status

onMounted(() => {
  connectionStatus.value = 'Attempting to connect...';
  console.log('Vue Component Mounted. Attempting to connect to WebSocket...');
  socket = new WebSocket(wsUrl);

  socket.onopen = (event) => {
    console.log('Vue WebSocket ONOPEN event:', event);
    connectionStatus.value = 'Connected';
    messages.value.push('Status: Connected to ' + wsUrl);
  };

  socket.onmessage = (event) => {
    console.log('Vue WebSocket ONMESSAGE event. Data:', event.data);
    messages.value.push('Server: ' + event.data);
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
    socket = null; // This makes subsequent socket operations fail the 'if (socket)' check
  };

  socket.onerror = (errorEvent) => { // errorEvent is more specific than 'error'
    console.error('Vue WebSocket ONERROR event:', errorEvent);
    connectionStatus.value = 'Error connecting';
    messages.value.push('Error: WebSocket error. See console for details.');
  };
});

onUnmounted(() => {
  console.log('Vue Component Unmounted. Closing WebSocket if open.');
  if (socket) {
    socket.close();
  }
});

const sendMessage = () => {
  console.log('--- sendMessage called ---');
  console.log('Current messageToSend:', messageToSend.value);
  console.log('Socket object:', socket);
  if (socket) {
    console.log('Socket readyState:', socket.readyState, '(OPEN is 1)');
  }

  if (messageToSend.value && socket && socket.readyState === WebSocket.OPEN) {
    socket.send(messageToSend.value);
    console.log('Message sent to server:', messageToSend.value);
    messages.value.push('You: ' + messageToSend.value);
    // Do NOT clear messageToSend.value here if you want to easily resend or see why it might fail
    // messageToSend.value = ''; // Let's comment this out for debugging
  } else {
    let blockReason = '';
    if (!messageToSend.value) blockReason += 'Message is empty. ';
    if (!socket) blockReason += 'Socket object is null. ';
    if (socket && socket.readyState !== WebSocket.OPEN) blockReason += `Socket readyState is ${socket.readyState}, not OPEN (1). `;
    console.log('Cannot send message. Reason:', blockReason.trim());
    messages.value.push('Status: Cannot send. ' + blockReason.trim());
  }
};
</script>

<template>
  <div>
    <h1>Vue WebSocket HUD Client</h1>
    <p>Status: {{ connectionStatus }}</p>

    <div>
      <input type="text" v-model="messageToSend" @keyup.enter="sendMessage" placeholder="Enter message" />
      <button @click="sendMessage">Send Message</button>
    </div>

    <div id="responses">
      <h2>Log:</h2>
      <ul>
        <li v-for="(msg, index) in messages" :key="index">{{ msg }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
/* Add some basic styling if you like */
#responses ul {
  list-style-type: none;
  padding: 0;
}
#responses li {
  background-color: #f0f0f0;
  margin-bottom: 5px;
  padding: 8px;
  border-radius: 4px;
}
</style>