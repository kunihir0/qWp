<template>
  <div class="small-gauge glass-panel">
    <div class="gauge-label">{{ label }}</div>
    <div class="gauge-value-container">
      <div class="gauge-value">{{ displayValue }}</div>
      <div class="gauge-unit">{{ unit }}</div>
    </div>
    <div class="gauge-bar-container">
      <div class="gauge-bar-background"></div>
      <div
        class="gauge-bar-fill"
        :class="barClass"
        :style="{ width: `${percentage}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  label: String,
  value: [Number, null],
  maxValue: Number,
  unit: String,
  barClass: String
});

const displayValue = computed(() => {
  if (props.value === null) return '---';
  return props.value?.toLocaleString() || '---';
});

const percentage = computed(() => {
  if (props.value === null || props.maxValue === null) return 0;
  return Math.min(100, Math.max(0, ((props.value || 0) / (props.maxValue || 100)) * 100));
});
</script>

<style scoped>
.small-gauge {
  background: rgba(25, 32, 45, 0.4);
  border-radius: var(--border-radius-md);
  border: 1px solid rgba(255, 255, 255, 0.07);
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.gauge-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: var(--spacing-sm);
}

.gauge-value-container {
  display: flex;
  align-items: baseline;
  margin-bottom: var(--spacing-sm);
}

.gauge-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-right: var(--spacing-sm);
}

.gauge-unit {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.gauge-bar-container {
  position: relative;
  height: 4px;
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.gauge-bar-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 2px;
  transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Glass panel style from existing components */
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
  transform: translateY(-1px);
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.25);
}
</style>