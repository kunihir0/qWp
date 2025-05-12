<script setup lang="ts">
defineProps<{
  lastError: string | null;
}>();
</script>

<template>
  <div v-if="lastError" class="error-message glass-panel">
    <div class="error-icon">⚠️</div>
    <div class="error-text">{{ lastError }}</div>
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

.error-message {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 12px var(--spacing-md);
  /* margin-bottom: var(--spacing-sm); App.vue will handle layout gap */
  background: rgba(229, 62, 62, 0.2); /* More pronounced error background */
  border-color: rgba(229, 62, 62, 0.4);
  color: var(--accent-danger); /* Ensure text is readable */
}

.error-icon {
  font-size: 1.5rem;
}

.error-text {
  font-weight: 600;
  flex-grow: 1;
  word-break: break-word; /* Ensure long errors wrap */
}
</style>