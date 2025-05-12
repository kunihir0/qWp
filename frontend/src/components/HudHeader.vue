<script setup lang="ts">
defineProps<{
  currentDateTime: string;
  currentUser: string;
  connectionStatus: 'connected' | 'connecting' | 'disconnected' | 'error';
  pulseActive: boolean;
}>();
</script>

<template>
  <div class="hud-header glass-panel">
    <div class="header-left">
      <h1>qWp</h1>
    </div>
    <div class="header-center">
      <div class="datetime">{{ currentDateTime }}</div>
    </div>
    <div class="header-right">
      <div class="user-info">
        <span class="user-name">{{ currentUser }}</span>
      </div>
      <div class="connection-status">
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
</template>

<style scoped>
/* Glassmorphism Style - ENHANCED - Copied from App.vue, can be centralized if used by many components */
.glass-panel {
  background: var(--glass-bg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(var(--blur-strength));
  -webkit-backdrop-filter: blur(var(--blur-strength));
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  padding: var(--spacing-md);
  width: 100%;
  box-sizing: border-box;
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
  flex-wrap: nowrap; /* Ensure header items don't wrap on smaller screens if possible */
  padding: var(--spacing-md);
  /* margin-bottom: var(--spacing-sm); Removed, App.vue will handle layout gap */
}

/* Tesla-inspired minimalist header styling */
.header-left h1 {
  font-size: 2rem;
  font-weight: 300; /* Lighter font weight for Tesla look */
  color: var(--text-primary);
  margin: 0;
  line-height: 1;
  letter-spacing: 2px; /* Increased spacing for that luxury feel */
}

.header-center .datetime {
  font-size: 1rem;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.user-info {
  display: flex;
  align-items: center;
}

.user-name {
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 400;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.status-dot.connected { background-color: var(--status-connected); }
.status-dot.connecting { background-color: var(--status-connecting); }
.status-dot.error { background-color: var(--status-error); }
.status-dot.disconnected { background-color: var(--status-disconnected); }

.status-dot.pulse {
  animation: pulse-animation 1.5s infinite;
}

@keyframes pulse-animation {
  0% { box-shadow: 0 0 0 0 rgba(var(--status-connected), 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(var(--status-connected), 0); }
  100% { box-shadow: 0 0 0 0 rgba(var(--status-connected), 0); }
}

/* Specific pulse colors if needed, or adjust JS to pass a color */
.status-dot.connected.pulse { animation-name: pulse-connected; }
.status-dot.connecting.pulse { animation-name: pulse-connecting; }
.status-dot.error.pulse { animation-name: pulse-error; }
/* Disconnected usually doesn't pulse, but can be added if needed */

@keyframes pulse-connected {
  0% { box-shadow: 0 0 0 0 var(--status-connected); }
  70% { box-shadow: 0 0 0 8px rgba(72, 187, 120, 0); } /* Using direct RGB for var(--status-connected) */
  100% { box-shadow: 0 0 0 0 rgba(72, 187, 120, 0); }
}
@keyframes pulse-connecting {
  0% { box-shadow: 0 0 0 0 var(--status-connecting); }
  70% { box-shadow: 0 0 0 8px rgba(246, 173, 85, 0); } /* Using direct RGB for var(--status-connecting) */
  100% { box-shadow: 0 0 0 0 rgba(246, 173, 85, 0); }
}
@keyframes pulse-error {
  0% { box-shadow: 0 0 0 0 var(--status-error); }
  70% { box-shadow: 0 0 0 8px rgba(229, 62, 62, 0); } /* Using direct RGB for var(--status-error) */
  100% { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0); }
}

/* Responsive adjustments for header */
@media (max-width: 768px) {
  .hud-header {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: stretch; /* Stretch items to full width */
  }
  .header-left, .header-center, .header-right {
    width: 100%;
    justify-content: space-between; /* Distribute items within each section */
  }
  .header-center {
    order: 1; /* Move datetime below title on small screens */
    text-align: center;
    margin-top: var(--spacing-sm);
  }
  .header-right {
    order: 2;
    margin-top: var(--spacing-sm);
  }
  .user-info, .connection-status {
    flex-grow: 1; /* Allow them to take available space */
    justify-content: center; /* Center their content */
  }
}

@media (max-width: 480px) {
  .header-left h1 {
    font-size: 1.5rem;
  }
  .user-name, .status-label, .status-indicator {
    font-size: 0.85rem;
  }
  .connection-status {
    flex-direction: column;
    align-items: center;
    gap: 5px;
  }
}
</style>