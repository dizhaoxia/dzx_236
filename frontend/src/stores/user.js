import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('vocab_token') || '',
    user: JSON.parse(localStorage.getItem('vocab_user') || 'null'),
    stats: null
  }),
  getters: {
    isLoggedIn: state => !!state.token,
    nickname: state => state.user?.nickname || '',
    dailyGoal: state => state.user?.daily_goal || 20
  },
  actions: {
    async login(email, password) {
      const res = await api.post('/auth/login', { email, password })
      if (res.code === 200) {
        this.token = res.data.token
        this.user = res.data.user
        localStorage.setItem('vocab_token', res.data.token)
        localStorage.setItem('vocab_user', JSON.stringify(res.data.user))
      }
      return res
    },
    async register(data) {
      const res = await api.post('/auth/register', data)
      if (res.code === 200) {
        this.token = res.data.token
        this.user = res.data.user
        localStorage.setItem('vocab_token', res.data.token)
        localStorage.setItem('vocab_user', JSON.stringify(res.data.user))
      }
      return res
    },
    logout() {
      this.token = ''
      this.user = null
      this.stats = null
      localStorage.removeItem('vocab_token')
      localStorage.removeItem('vocab_user')
    },
    async fetchProfile() {
      const res = await api.get('/auth/profile')
      if (res.code === 200 && res.data.user) {
        this.user = res.data.user
        this.stats = res.data.stats
        localStorage.setItem('vocab_user', JSON.stringify(res.data.user))
      }
      return res
    },
    async updateProfile(data) {
      const res = await api.put('/auth/profile', data)
      if (res.code === 200) {
        this.user = { ...this.user, ...res.data }
        localStorage.setItem('vocab_user', JSON.stringify(this.user))
      }
      return res
    }
  }
})
