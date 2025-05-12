<script setup lang="ts">
defineProps<{
  milActive: boolean;
  dtcCount: number;
}>();
</script>

<template>
  <div v-if="milActive" class="mil-warning glass-panel">
    <div class="mil-icon">🚨</div>
    <div class="mil-text">
      Check Engine Light ON - {{ dtcCount }} diagnostic trouble code{{ dtcCount !== 1 ? 's' : '' }} detected
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

.mil-warning {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 12px var(--spacing-md);
  /* margin-bottom: var(--spacing-sm); App.vue will handle layout gap */
  background: rgba(229, 62, 62, 0.15); /* From original App.vue */
  border-color: rgba(229, 62, 62, 0.3); /* From original App.vue */
  animation: pulse-warn 1.5s infinite; /* From original App.vue */
}

.mil-icon {
  font-size: 1.5rem; /* From original App.vue */
}

.mil-text {
  font-weight: 600;
  color: #fbd38d; /* From original App.vue */
}

@keyframes pulse-warn { /* From original App.vue */
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}
</style>