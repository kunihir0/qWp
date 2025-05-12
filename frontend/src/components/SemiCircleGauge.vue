<template>
  <div class="semi-circle-gauge glass-panel">
    <div class="gauge-label">{{ label }}</div>
    <div class="gauge-value">{{ displayValue }}</div>
    <div class="gauge-unit">{{ unit }}</div>
    <div class="gauge-container">
      <svg class="gauge-svg" viewBox="0 0 200 120">
        <!-- Background track -->
        <path
          class="gauge-track"
          d="M10,110 A100,100 0 0,1 190,110"
          stroke="rgba(255,255,255,0.1)"
          stroke-width="10"
          fill="none"
        />
        
        <!-- Colored arc that shows the current value -->
        <path
          class="gauge-progress"
          :class="progressClass"
          :d="arcPath"
          :stroke="`url(#${gradientId})`"
          stroke-width="10"
          stroke-linecap="round"
          fill="none"
        />
        
        <!-- Gauge ticks -->
        <g class="gauge-ticks">
          <line
            v-for="tick in renderedTicks"
            :key="tick.angle"
            :x1="tick.x1"
            :y1="tick.y1"
            :x2="tick.x2"
            :y2="tick.y2"
            class="tick"
            :class="{'major-tick': tick.major}"
          />
        </g>
        
        <!-- Tick labels -->
        <g class="gauge-labels">
          <text
            v-for="label in tickLabels"
            :key="label.value"
            :x="label.x"
            :y="label.y"
            class="tick-label"
          >{{ label.text }}</text>
        </g>
        
        <!-- Needle -->
        <g class="gauge-needle" :style="{ transform: `rotate(${needleRotation}deg)`, 'transform-origin': '100px 110px' }">
          <line x1="100" y1="110" x2="100" y2="30" stroke="var(--text-primary)" stroke-width="2" />
          <circle cx="100" cy="110" r="5" fill="var(--text-primary)" />
        </g>
        
        <!-- Gradient definition -->
        <defs>
          <linearGradient :id="gradientId" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop :stop-color="startColor" offset="0%" />
            <stop :stop-color="endColor" offset="100%" />
          </linearGradient>
        </defs>
      </svg>
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
  startColor: {
    type: String,
    default: 'rgba(255,255,255,0.7)'
  },
  endColor: {
    type: String,
    default: 'rgba(255,255,255,0.7)'
  },
  progressClass: String,
  majorTicks: {
    type: Number,
    default: 5
  },
  minorTicks: {
    type: Number,
    default: 20
  }
});

// Generate a unique ID for the gradient
const gradientId = computed(() => `gauge-gradient-${props.label?.toLowerCase().replace(/\s+/g, '-') || 'default'}`);

// Display value with proper formatting
const displayValue = computed(() => {
  if (props.value === null) return '---';
  return props.value?.toLocaleString() || '---';
});

// Calculate the percentage of the current value relative to max
const percentage = computed(() => {
  if (props.value === null || props.maxValue === null) return 0;
  return Math.min(100, Math.max(0, ((props.value || 0) / (props.maxValue || 100)) * 100));
});

// Calculate the sweep angle based on percentage (0 to 180 degrees)
const sweepAngle = computed(() => {
  return (percentage.value / 100) * 180;
});

// Calculate the needle rotation angle
const needleRotation = computed(() => {
  return (percentage.value / 100) * 180 - 90;
});

// Generate the SVG path for the arc
const arcPath = computed(() => {
  // If value is 0, return empty path
  if (percentage.value === 0) return '';
  
  const startAngle = -180;
  const endAngle = startAngle + sweepAngle.value;
  
  // Convert angles to radians
  const startRad = (startAngle * Math.PI) / 180;
  const endRad = (endAngle * Math.PI) / 180;
  
  // Calculate start and end points
  const radius = 100;
  const cx = 100;
  const cy = 110;
  
  const x1 = cx + radius * Math.cos(startRad);
  const y1 = cy + radius * Math.sin(startRad);
  const x2 = cx + radius * Math.cos(endRad);
  const y2 = cy + radius * Math.sin(endRad);
  
  // Use a large arc if angle > 180 degrees
  const largeArcFlag = sweepAngle.value > 180 ? 1 : 0;
  
  return `M${x1},${y1} A${radius},${radius} 0 ${largeArcFlag},1 ${x2},${y2}`;
});

// Generate tick marks
const renderedTicks = computed(() => {
  const ticks = [];
  const totalTicks = props.minorTicks || 20;
  const majorTicks = props.majorTicks || 5;
  const radius = 100;
  const cx = 100;
  const cy = 110;
  const majorTickLength = 15;
  const minorTickLength = 7;
  
  for (let i = 0; i <= totalTicks; i++) {
    const angle = -180 + (i / totalTicks) * 180;
    const rad = (angle * Math.PI) / 180;
    const isMajorTick = i % (totalTicks / majorTicks) === 0;
    
    const tickLength = isMajorTick ? majorTickLength : minorTickLength;
    
    const x1 = cx + radius * Math.cos(rad);
    const y1 = cy + radius * Math.sin(rad);
    const x2 = cx + (radius - tickLength) * Math.cos(rad);
    const y2 = cy + (radius - tickLength) * Math.sin(rad);
    
    ticks.push({
      x1, y1, x2, y2,
      major: isMajorTick,
      angle
    });
  }
  
  return ticks;
});

// Generate tick labels
const tickLabels = computed(() => {
  const labels = [];
  const totalLabels = (props.majorTicks || 5) + 1;
  const maxValue = props.maxValue || 100;
  const radius = 75;
  const cx = 100;
  const cy = 110;
  
  for (let i = 0; i < totalLabels; i++) {
    const value = (i / (totalLabels - 1)) * maxValue;
    const angle = -180 + (i / (totalLabels - 1)) * 180;
    const rad = (angle * Math.PI) / 180;
    
    const x = cx + (radius - 20) * Math.cos(rad);
    const y = cy + (radius - 20) * Math.sin(rad);
    
    labels.push({
      value,
      text: Math.round(value).toLocaleString(),
      x,
      y
    });
  }
  
  return labels;
});
</script>

<style scoped>
.semi-circle-gauge {
  background: rgba(25, 32, 45, 0.4);
  border-radius: var(--border-radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.07);
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.gauge-label {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: var(--spacing-sm);
}

.gauge-value {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.gauge-unit {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin-top: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.gauge-container {
  width: 100%;
  position: relative;
}

.gauge-svg {
  width: 100%;
  height: auto;
}

.gauge-track {
  transition: all 0.3s ease;
}

.gauge-progress {
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.tick {
  stroke: rgba(255, 255, 255, 0.3);
  stroke-width: 1;
}

.major-tick {
  stroke: rgba(255, 255, 255, 0.6);
  stroke-width: 2;
}

.tick-label {
  fill: var(--text-secondary);
  font-size: 0.7rem;
  text-anchor: middle;
  alignment-baseline: middle;
}

.gauge-needle {
  transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
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
  transform: translateY(-2px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}
</style>