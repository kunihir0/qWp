<script setup lang="ts">
interface Tick {
  position: number;
  value: number;
}

defineProps<{
  label: string;
  value: string;
  unit: string;
  percentage: number;
  maxValue: number;
  ticks: Tick[];
  barClass?: string;
  valueClass?: string;
}>();

// Helper to generate scale labels, assuming 6 labels (0, 20%, 40%, 60%, 80%, 100% of maxValue)
// This can be made more dynamic if needed, or passed as a prop
const scaleLabels = (maxValue: number) => {
  const labels = [];
  for (let i = 0; i <= 5; i++) { // 0 to 5 for 6 labels
    labels.push({
      position: i * 20, // 0%, 20%, ..., 100%
      value: Math.round((i / 5) * maxValue)
    });
  }
  return labels;
};
</script>

<template>
  <div class="gauge glass-panel">
    <div class="gauge-header">
      <div class="gauge-label">{{ label }}</div>
      <div class="gauge-range">0 - {{ maxValue.toLocaleString() }}{{ unit === '%' ? '%' : '' }}</div>
    </div>
    <div class="gauge-display">
      <div class="gauge-value" :class="valueClass">{{ value }}</div>
      <div class="gauge-unit">{{ unit }}</div>
    </div>
    <div class="gauge-bar-container">
      <div class="gauge-bar-background"></div>
      <div
        class="gauge-bar-fill"
        :style="{ width: `${percentage}%` }"
        :class="[barClass, { 'high': percentage > 80 && !barClass?.includes('temperature-fill') && !barClass?.includes('fuel-fill') }]"
      ></div>
      <div class="gauge-ticks">
        <div
          v-for="(tick, i) in ticks"
          :key="`${label}-tick-${i}`"
          class="gauge-tick"
          :style="{ left: `${tick.position}%` }"
        ></div>
      </div>
    </div>
    <div class="gauge-scale">
      <span v-for="(tick, i) in scaleLabels(maxValue)" :key="`${label}-scale-label-${i}`"
          :style="{ left: `${tick.position}%` }">
        {{ tick.value.toLocaleString() }}{{ unit === '%' && label !== 'Fuel Level' ? '%' : '' }}
      </span>
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
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-panel:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}

.gauge {
  display: flex;
  flex-direction: column;
  min-width: 0; /* Prevent flexbox overflow */
  min-height: 200px; /* Maintain a minimum height */
  width: 100%;
  padding: var(--spacing-md);
}

.gauge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
  flex-wrap: wrap; /* Allow wrapping for smaller displays */
  width: 100%;
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
  margin-bottom: var(--spacing-md);
}

.gauge-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin-right: var(--spacing-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  /* Default color, can be overridden by valueClass */
  color: var(--text-primary);
}

.gauge-unit {
  font-size: 1.1rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.gauge-bar-container {
  position: relative;
  height: 16px; /* Standard bar height */
  margin-bottom: 30px; /* Space for scale */
  width: 100%;
  overflow: hidden; /* Clip fill bar */
  border-radius: 8px; /* Rounded bar ends */
  background: rgba(0, 0, 0, 0.3); /* Darker background for contrast */
}

.gauge-bar-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3); /* Consistent with container or slightly different */
  border-radius: 8px;
}

.gauge-bar-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: 8px;
  transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1); /* Smooth animation */
  max-width: 100%; /* Ensure it doesn't exceed container */
  /* Default fill, specific fills via barClass */
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
}

/* Default alert state for generic gauges */
.gauge-bar-fill.high {
  background: linear-gradient(90deg, var(--accent-warning), var(--accent-danger));
}

/* Specific gauge styling via barClass prop */
/* RPM */
.rpm-value { color: var(--rpm-gradient-end); }
.rpm-fill { background: linear-gradient(90deg, var(--rpm-gradient-start), var(--rpm-gradient-end)); }

/* Speed */
.speed-value { color: var(--speed-gradient-end); }
.speed-fill { background: linear-gradient(90deg, var(--speed-gradient-start), var(--speed-gradient-end)); }

/* Engine Load */
.engine-load-fill { background: linear-gradient(90deg, var(--engine-load-gradient-start), var(--engine-load-gradient-end)); }

/* Throttle */
.throttle-fill { background: linear-gradient(90deg, var(--throttle-gradient-start), var(--throttle-gradient-end)); }

/* Temperature specific styling */
.temperature-fill {
  background: linear-gradient(90deg, var(--temp-normal-gradient-start), var(--temp-normal-gradient-end)) !important;
}
.temperature-fill.warning { /* This class would be added dynamically based on percentage in App.vue or here */
  background: linear-gradient(90deg, var(--temp-warning-gradient-start), var(--temp-warning-gradient-end)) !important;
}
.temperature-fill.high { /* This class would be added dynamically */
  background: linear-gradient(90deg, var(--temp-high-gradient-start), var(--temp-high-gradient-end)) !important;
  animation: pulse-warn 1.5s infinite;
}

.gauge-ticks {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none; /* Ticks should not be interactive */
}

.gauge-tick {
  position: absolute;
  width: 2px;
  height: 100%; /* Full height of the bar */
  background: rgba(255, 255, 255, 0.2); /* Subtle tick marks */
  transform: translateX(-50%); /* Center the tick */
}

.gauge-scale {
  position: relative; /* For absolute positioning of span elements */
  width: 100%;
  height: 24px; /* Height for the scale numbers */
  margin-top: var(--spacing-sm); /* Space between bar and scale */
  overflow: hidden; /* Prevent text overflow issues */
}

.gauge-scale span {
  position: absolute;
  transform: translateX(-50%); /* Center the text under the tick position */
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap; /* Prevent wrapping of scale numbers */
}

@keyframes pulse-warn {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}
</style>