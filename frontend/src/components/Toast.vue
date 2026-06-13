<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div
        v-for="t in toastStore.toasts"
        :key="t.id"
        class="toast-item"
        :class="`toast-${t.type}`"
      >
        <span class="toast-icon">{{ getIcon(t.type) }}</span>
        <span class="toast-message">{{ t.message }}</span>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

const getIcon = (type) => {
  const icons = {
    success: '✅',
    error: '❌',
    info: 'ℹ️',
    warning: '⚠️'
  }
  return icons[type] || 'ℹ️'
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 84px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast-item {
  padding: 12px 18px;
  border-radius: 10px;
  color: white;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 240px;
  font-size: 14px;
  font-weight: 500;
}

.toast-success { background: var(--success); }
.toast-error { background: var(--danger); }
.toast-info { background: var(--info); }
.toast-warning { background: var(--warning); }

.toast-icon { font-size: 16px; }

.toast-enter-active {
  animation: toast-in 0.3s ease;
}
.toast-leave-active {
  animation: toast-out 0.3s ease;
}

@keyframes toast-in {
  from { transform: translateX(120%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes toast-out {
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(120%); opacity: 0; }
}
</style>
