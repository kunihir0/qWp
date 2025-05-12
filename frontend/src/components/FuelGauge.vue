<script setup lang="ts">
defineProps<{
  displayFuelLevel: string;
  fuelLevelUnit: string;
  fuelLevelPercentage: number;
}>();
</script>

<template>
  <div class="gauge fuel-gauge glass-panel">
    <div class="gauge-header">
      <div class="gauge-label">Fuel Level</div>
    </div>
    <div class="gauge-display">
      <div class="gauge-value">{{ displayFuelLevel }}</div>
      <div class="gauge-unit">{{ fuelLevelUnit }}</div>
    </div>
    <div class="fuel-indicator-container">
      <div class="fuel-icon">⛽</div>
      <div class="fuel-bar-container">
        <div class="gauge-bar-background"></div>
        <div
          class="gauge-bar-fill fuel-fill"
          :style="{ width: `${fuelLevelPercentage}%` }"
          :class="{ 'low': fuelLevelPercentage < 20 }"
        ></div>
      </div>
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

.gauge {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: var(--spacing-md);
}

.fuel-gauge {
  min-height: 150px; /* From original App.vue */
}

.gauge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
  flex-wrap: wrap;
  width: 100%;
}

.gauge-label {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.gauge-display {
  display: flex;
  align-items: baseline;
  margin-bottom: var(--spacing-sm); /* Adjusted from var(--spacing-md) for tighter layout */
}

.gauge-value {
  font-size: 2.5rem; /* Consistent with DataGauge */
  font-weight: 700;
  margin-right: var(--spacing-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary); /* Default color */
}

.gauge-unit {
  font-size: 1.1rem; /* Consistent with DataGauge */
  color: var(--text-secondary);
  white-space: nowrap;
}

.fuel-indicator-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm); /* From original App.vue */
  width: 100%;
}

.fuel-icon {
  font-size: 1.5rem; /* From original App.vue */
  margin-right: var(--spacing-sm); /* From original App.vue */
}

.fuel-bar-container {
  position: relative;
  height: 20px; /* From original App.vue */
  flex-grow: 1;
  border-radius: 10px; /* From original App.vue */
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3); /* From original App.vue */
}

.gauge-bar-background { /* Re-using class from DataGauge for consistency */
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3); /* Consistent with container or slightly different */
  border-radius: 10px; /* Match fuel-bar-container */
}

.gauge-bar-fill { /* Re-using class from DataGauge for consistency */
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: 10px; /* Match fuel-bar-container */
  transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
  max-width: 100%;
}

.fuel-fill { /* Specific styling for fuel */
  background: linear-gradient(90deg, var(--fuel-normal-gradient-start), var(--fuel-normal-gradient-end)); /* From original App.vue */
}

.fuel-fill.low {
  background: linear-gradient(90deg, var(--fuel-low-gradient-start), var(--fuel-low-gradient-end)); /* From original App.vue */
  animation: pulse-warn 1.5s infinite; /* From original App.vue */
}

@keyframes pulse-warn { /* From original App.vue */
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}
</style>