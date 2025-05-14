<script setup lang="ts">
defineProps({
  vehicleMake: {
    type: String,
    default: 'N/A'
  },
  vehicleYear: {
    type: [Number, String], // Allow string for 'N/A'
    default: 'N/A'
  },
  vin: {
    type: String,
    default: 'N/A'
  }
});
</script>

<template>
  <div class="vehicle-model-placeholder glass-panel">
    <div class="model-container">
      <div class="model-label">
        {{ vehicleMake }} {{ vehicleYear !== 'N/A' ? `(${vehicleYear})` : '' }}
      </div>
      <div class="model-placeholder">
        <div class="car-silhouette"></div>
        <span class="placeholder-text">{{ vin !== 'N/A' ? `VIN: ${vin}` : 'Vehicle Information' }}</span>
      </div>
      <div v-if="vehicleMake === 'N/A' && vin === 'N/A'" class="info-unavailable">
        Vehicle data not available
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
  padding: var(--spacing-md); /* Adjusted from 0 in App.vue for consistency */
  width: 100%;
  box-sizing: border-box;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-panel:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}

/* Vehicle Model Placeholder */
.vehicle-model-placeholder {
  height: auto;
  min-height: 250px; /* Taller to match side gauges */
  background: rgba(20, 20, 20, 0.5); /* Slightly more visible than other panels */
  border: 1px solid rgba(255, 255, 255, 0.07);
  overflow: hidden;
}

.model-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  width: 100%;
  /* padding: var(--spacing-md); Removed, glass-panel now has padding */
}

.model-label {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm); /* Reduced margin */
  text-transform: uppercase;
  letter-spacing: 1.5px;
  text-align: center; /* Center the make/year */
}

.model-placeholder {
  flex: 1; /* Take remaining space */
  min-height: 150px; /* Ensure space for silhouette */
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
  padding: var(--spacing-sm); /* Add some internal padding */
}

/* Car silhouette */
.car-silhouette {
  width: 70%; /* Larger vehicle representation */
  height: 60%; /* Taller representation */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512' fill='%23ffffff' opacity='0.7'%3E%3Cpath d='M120 32C53.8 32 0 85.8 0 152v144c0 26.5 21.5 48 48 48h32c17.7 0 32-14.3 32-32V227.3c0-15.5-15.1-26.7-29.8-21.9L43.8 224c-9 3-14.7-8.5-7.3-14.7L71.3 181 88.8 166.6c37.2-32.9 85.5-50.6 135.6-50.6H287.4c50.1 0 98.4 17.7 135.6 50.6L440.7 181l34.9 28.3c7.4 6.2 1.7 17.7-7.3 14.7l-38.4-18.6c-14.7-4.8-29.8 6.4-29.8 21.9v84.7c0 17.7 14.3 32 32 32h32c26.5 0 48-21.5 48-48V152C512 85.8 458.2 32 392 32H120zm200 280c0 13.3-10.7 24-24 24H216c-13.3 0-24-10.7-24-24s10.7-24 24-24h80c13.3 0 24 10.7 24 24zM80 304c13.3 0 24 10.7 24 24s-10.7 24-24 24-24-10.7-24-24 10.7-24 24-24zm352 0c13.3 0 24 10.7 24 24s-10.7 24-24 24-24-10.7-24-24 10.7-24 24-24z'/%3E%3C/svg%3E");
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  margin-bottom: var(--spacing-md);
}

.placeholder-text {
  font-size: 0.85rem; /* Slightly smaller VIN text */
  color: var(--text-secondary);
  letter-spacing: 1px;
  position: relative;
  z-index: 2;
  padding: var(--spacing-xs) 10px; /* Adjusted padding */
  text-align: center;
  text-transform: uppercase;
  font-weight: 400;
  word-break: break-all; /* Break long VINs */
}

.info-unavailable {
  margin-top: var(--spacing-sm);
  font-size: 0.8rem;
  color: var(--text-dim);
}
</style>