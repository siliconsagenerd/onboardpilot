import axios from 'axios'

const base =
  (import.meta as any).env?.VITE_API_BASE_URL ||
  (import.meta as any).env?.VITE_API_BASE ||
  (import.meta.env.PROD ? '' : 'http://localhost:8000')

if (import.meta.env.PROD && !((import.meta as any).env?.VITE_API_BASE_URL || (import.meta as any).env?.VITE_API_BASE)) {
  console.warn('VITE_API_BASE_URL is not set; using same-origin requests')
}

export const api = axios.create({ baseURL: base })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)
