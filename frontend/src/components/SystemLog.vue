<script setup lang="ts">
defineProps<{
  messages: string[];
}>();
</script>

<template>
  <div class="system-log glass-panel">
    <div class="log-header">
      <h2>System Messages</h2>
    </div>
    <div class="log-container">
      <ul class="log-messages">
        <li v-for="(msg, index) in messages.slice().reverse().slice(0, 6)" :key="index"
            :class="{
              'error-log': msg.toLowerCase().includes('error'),
              'connect-log': msg.toLowerCase().includes('connect') && !msg.toLowerCase().includes('error'),
              'disconnect-log': msg.toLowerCase().includes('disconnect') || msg.toLowerCase().includes('lost'),
              'status-log': msg.toLowerCase().includes('status:')
            }">
          {{ msg }}
        </li>
        <li v-if="!messages || messages.length === 0" class="placeholder-log">
          No messages yet. Waiting for data...
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.glass-panel {
  background: var(--glass-bg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(var(--blur-strength));
  -webkit-backdrop-filter: blur(var(--blur-strength));
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  padding: var(--spacing-md);
  width: 100%;
  box-sizing: border-box;
}

.system-log {
  width: 100%;
  overflow: hidden; /* From original App.vue */
}

.log-header {
  margin-bottom: var(--spacing-sm);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--glass-border);
}

.log-header h2 {
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.log-container {
  max-height: 150px; /* Limit height for recent messages */
  overflow-y: auto;
  padding-right: 5px; /* Space for scrollbar */
}

/* Custom scrollbar for log container */
.log-container::-webkit-scrollbar {
  width: 8px;
}

.log-container::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.1);
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb {
  background: var(--text-secondary);
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: var(--accent-primary);
}

.log-messages {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.log-messages li {
  padding: 6px 0;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
  line-height: 1.4;
  word-break: break-word;
}

.log-messages li:last-child {
  border-bottom: none;
}

.log-messages .error-log {
  color: var(--accent-danger);
  font-weight: 600;
}

.log-messages .connect-log {
  color: var(--status-connected);
}
.log-messages .disconnect-log {
  color: var(--accent-warning);
}
.log-messages .status-log {
  color: var(--accent-secondary);
}


.placeholder-log {
  font-style: italic;
  text-align: center;
  padding: var(--spacing-md) 0;
}
</style>