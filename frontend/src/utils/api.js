import axios from 'axios'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('vocab_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('vocab_token')
      localStorage.removeItem('vocab_user')
      if (router.currentRoute.value.name !== 'Login') {
        router.push({ name: 'Login' })
      }
    }
    return Promise.reject(error.response?.data || error)
  }
)

export default api
