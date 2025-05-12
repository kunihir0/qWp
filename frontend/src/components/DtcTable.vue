<script setup lang="ts">
interface DtcCode {
  code: string;
  desc: string;
}

defineProps<{
  dtcCodes: DtcCode[];
  milActive: boolean; // To control visibility, though parent might handle v-if
  dtcCount: number;   // To control visibility, though parent might handle v-if
}>();
</script>

<template>
  <div v-if="milActive && dtcCount > 0" class="dtc-section glass-panel">
    <div class="dtc-header">
      <h2>Diagnostic Trouble Codes (DTCs)</h2>
    </div>
    <div class="dtc-list-container">
      <table class="dtc-table">
        <thead>
          <tr>
            <th>Code</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(dtc, index) in dtcCodes" :key="`dtc-${index}`">
            <td class="dtc-code">{{ dtc.code }}</td>
            <td class="dtc-desc">{{ dtc.desc }}</td>
          </tr>
          <tr v-if="!dtcCodes || dtcCodes.length === 0">
            <td colspan="2" class="dtc-empty">No detailed DTC information available</td>
          </tr>
        </tbody>
      </table>
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

.dtc-section {
  /* margin-top: var(--spacing-md); App.vue will handle layout gap */
  overflow: hidden; /* From original App.vue */
  width: 100%;
}

.dtc-header {
  margin-bottom: var(--spacing-sm);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--glass-border);
}

.dtc-header h2 {
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.dtc-list-container {
  max-height: 250px; /* Limit height and make scrollable */
  overflow-y: auto;
  border-radius: var(--border-radius-sm);
  background-color: rgba(0,0,0,0.1); /* Slight background for the scrollable area */
}

/* Custom scrollbar for DTC list */
.dtc-list-container::-webkit-scrollbar {
  width: 8px;
}

.dtc-list-container::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.2);
  border-radius: 4px;
}

.dtc-list-container::-webkit-scrollbar-thumb {
  background: var(--accent-secondary);
  border-radius: 4px;
}

.dtc-list-container::-webkit-scrollbar-thumb:hover {
  background: var(--accent-primary);
}

.dtc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.dtc-table th,
.dtc-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--glass-border);
}

.dtc-table th {
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: sticky; /* Make header sticky */
  top: 0;
  z-index: 1;
}

.dtc-table tbody tr:last-child td {
  border-bottom: none;
}

.dtc-table tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.dtc-code {
  font-weight: 700;
  color: var(--accent-warning);
  min-width: 80px; /* Ensure code column has some width */
}

.dtc-desc {
  color: var(--text-primary);
  word-break: break-word;
}

.dtc-empty {
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  padding: var(--spacing-md) 0;
}
</style>