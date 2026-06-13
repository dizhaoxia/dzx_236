import { defineStore } from 'pinia'

let toastId = 0

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: []
  }),
  actions: {
    add(message, type = 'info', duration = 3000) {
      const id = ++toastId
      this.toasts.push({ id, message, type })
      setTimeout(() => {
        this.remove(id)
      }, duration)
      return id
    },
    remove(id) {
      const idx = this.toasts.findIndex(t => t.id === id)
      if (idx > -1) this.toasts.splice(idx, 1)
    },
    success(message, duration) { return this.add(message, 'success', duration) },
    error(message, duration) { return this.add(message, 'error', duration) },
    info(message, duration) { return this.add(message, 'info', duration) },
    warning(message, duration) { return this.add(message, 'warning', duration) }
  }
})
